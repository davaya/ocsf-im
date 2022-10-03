import fire
import jadn
import json
import os
from pathlib import Path
import shutil
from io import TextIOWrapper
from urllib.request import urlopen, Request
from urllib.parse import urlparse

"""
Convert a set of OCSF files into a JADN information model (IM).

An IM (abstract schema) validates messages in multiple data formats.
The framework files can be read directly from the OCSF repo or from a local clone. 
"""

OCSF_DIR = '../ocsf-schema'
OCSF_REPO = 'https://api.github.com/repos/ocsf/ocsf-schema/contents/'
OCSF_ROOT = OCSF_DIR       # select local or remote location for framework files
OUTPUT_DIR = 'Out'

# GitHubToken should contain a GitHub personal access token with only public_repo scope to avoid rate limiting
AUTH = {'Authorization': f'token {os.environ["GitHubToken"]}'} if OCSF_ROOT == OCSF_REPO else {}


class WebDirEntry:
    """
    Fake os.DirEntry type for GitHub filesystem
    """
    def __init__(self, name, etype, path, url):
        self.name = name
        self.etype = etype
        self.is_dir = lambda: self.etype == 'dir'
        self.path = path
        self.url = url


def scandir(path: str) -> list:
    """
    Return directory contents as a list of os.DirEntry (local) or WebDirEntry (GitHub) instances
    """
    u = urlparse(path)
    dlist = []
    try:
        if all([u.scheme, u.netloc]):
            with urlopen(Request(path, headers=AUTH)) as d:
                for dl in json.loads(d.read().decode()):
                    url = 'url' if dl['type'] == 'dir' else 'download_url'
                    dlist += [WebDirEntry(dl['name'], dl['type'], dl['url'], dl[url])]
        else:
            with os.scandir(path) as sl:
                dlist = [s for s in sl]
    except FileNotFoundError as e:
        pass
    return dlist


def relname(base, path: str) -> str:
    return Path(os.path.relpath(path.split('?')[0], base)).as_posix()


def load_ocsf(root: str) -> dict:
    ocsf = {'.': {}}
    dlist = scandir(root)
    for dl in dlist:
        if dl.name in ('version.json', 'categories.json', 'dictionary.json'):
            ocsf['.'].update({dl.name: load_json(dl)})
    if ocsf['.']:
        for dn in ('enums', 'events', 'includes', 'objects', 'profiles', 'templates'):
            print(f'    {dn}...')
            ocsf.update({dn: load_dir(f'{root}/{dn}', f'{root}/{dn}')})
        print('  Extensions:')
        ocsf['extensions'] = load_ocsf(f'{root}/extensions')
    return ocsf


def dump_ocsf(ocsf: dict, root: str) -> None:
    for fn in ('version.json', 'categories.json', 'dictionary.json'):
        dump_json(ocsf['.'][fn], os.path.join(root, fn))
    for dn in ('enums', 'events', 'includes', 'objects', 'extensions', 'profiles', 'templates'):
        dump_dir(ocsf[dn], os.path.join(root, dn))


def load_dir(base, path: str) -> dict:
    o = {}
    for entry in scandir(path):
        if entry.is_dir():
            o.update(load_dir(base, entry.path))
        elif os.path.splitext(entry.name)[1] == '.json':
            o.update({relname(base, entry.path): load_json(entry)})
        else:
            print(f'  File {entry.path} ignored')
    return o


def dump_dir(o: dict, root: str) -> None:
    for k, v in o.items():
        path = os.path.join(*k.split('/'))
        fpath = os.path.join(root, *os.path.split(path))
        if os.path.splitext(path)[1] == '.json':
            os.makedirs(os.path.join(root, *os.path.split(path)[:-1]), exist_ok=True)
            dump_json(v, fpath)
        else:
            os.makedirs(fpath, exist_ok=True)
            dump_dir(v, path)


def load_json(dl: os.DirEntry) -> dict:
    if hasattr(dl, 'url'):
        return json.load(TextIOWrapper(urlopen(Request(dl.url, headers=AUTH)), encoding='utf8'))
    else:
        try:
            with open(dl.path) as fp:
                return json.load(fp)
        except json.JSONDecodeError as e:
            print(f'Error: {dl.path}: {e}')
            return {}


def dump_json(d: dict, file: str) -> None:
    with open(file, 'w') as fp:
        json.dump(d, fp, indent=2)
        fp.write('\n')


def make_jadn(ocsf: dict) -> dict:
    """
    Construct a JADN Information Model (abstract schema) from the OCSF Framework data
    """
    def filename_to_typename(fn: str) -> str:
        return os.path.splitext(fn)[0].capitalize()

    def caption_to_fieldname(cap: str) -> str:
        return cap.lower().replace(' ', '_')

    def obj_enum_to_typename(object_name: str, attr_name: str) -> str:
        return '???'

    def caption_to_typename(cap: str) -> str:
        return cap.replace(' ', '-').capitalize()

    def name_to_typename(vname: str, attr_name: str) -> str:
        return f'{vname}_{attr_name.removesuffix("_id")}'.capitalize()

    def get_enum(enum: dict) -> list:
        it = []
        for k, v in enum.items():
            it.append([int(k), caption_to_fieldname(v['caption']), f'{v["caption"]}: {v.get("description", "")}'])
        return sorted(it)

    def make_category_enum(categories: dict) -> list:
        items = [[v['uid'], k, f'{v["caption"]}: {v["description"]}'] for k, v in categories['attributes'].items()]
        return [[categories['caption'], 'Enumerated', [], categories['description'], items]]

    def make_dictionary_enums(dictionary: dict) -> list:
        assert set(dictionary) - {'caption', 'description', 'name', 'attributes', 'types'} == set()
        types = []
        for k, v in dictionary['attributes'].items():
            if 'enum' in v:
                ename = v['sibling'] if 'sibling' in v else k
                types.append([ename.capitalize(), 'Enumerated', [], v['description'], get_enum(v['enum'])])
        return types

    def make_enums(enums: dict) -> list:
        """
        Make Enumerated types from files in "enums" directory, applying "defaults.json" values to each.
        """
        defaults = []
        types = []
        if 'defaults.json' in enums:
            defaults = get_enum(enums['defaults.json']['enum'])
        for fn, fv in enums.items():
            if fn != 'defaults.json':
                assert list(fv) == ["enum"]   # enum is the only property
                types.append([filename_to_typename(fn), 'Enumerated', [], '', defaults + get_enum(fv['enum'])])
        return types

    def make_events(events: dict) -> list:
        types = []
        eprops = {}
        for etype, evalue in events.items():
            eprops.update({evalue['uid']: evalue['name']} if 'uid' in evalue else {})
            for k, v in evalue['attributes'].items():
                if k == '$include':
                    pass
                elif e := v.pop('enum', ''):
                    types.append([name_to_typename(evalue['name'], k), 'Enumerated', [], '', get_enum(e)])
                print(k)
        return types

    pkg = {
        'info': {'package': f'https://ocsf.io/im/{ocsf["."]["version.json"]["version"]}'},
        'types': []
    }
    pkg['types'] += make_category_enum(ocsf['.']['categories.json'])
    pkg['types'] += make_dictionary_enums(ocsf['.']['dictionary.json'])
    pkg['types'] += make_enums(ocsf['enums'])
    pkg['types'] += make_events(ocsf['events'])
    return pkg


def generate_ocsf(jadn_pkg: dict) -> dict:
    o = {'version.json': {'version': jadn_pkg['info']['package'].split('/')[-1]}}
    return o


def create_im(ocsf_dir: str = OCSF_ROOT, output_dir: str = OUTPUT_DIR) -> None:
    print(f'JADN Version: {jadn.__version__}')
    ocsf = load_ocsf(ocsf_dir)
    print(f'OCSF Version: {ocsf["."]["version.json"]["version"]}')
    jadn_pkg = make_jadn(ocsf)
    os.makedirs(css_dir := os.path.join(output_dir, 'css'), exist_ok=True)
    shutil.copy(os.path.join(jadn.data_dir(), 'dtheme.css'), css_dir)
    output_name = 'ocsf'
    jadn.dump(jadn_pkg, os.path.join(output_dir, f'{output_name}.jadn'))
    jadn.convert.jidl_dump(jadn_pkg, os.path.join(output_dir, f'{output_name}.jidl'), style={'desc': 40})
    jadn.convert.markdown_dump(jadn_pkg, os.path.join(output_dir, f'{output_name}.md'))
    jadn.convert.html_dump(jadn_pkg, os.path.join(output_dir, f'{output_name}.html'))
    jadn.translate.json_schema_dump(jadn_pkg, os.path.join(output_dir, f'{output_name}.json'))

    # Copy relevant OCSF files to enable diff with generated files.
    os.makedirs(copy_dir := os.path.join(output_dir, 'ocsf-copy'), exist_ok=True)
    dump_ocsf(ocsf, copy_dir)
    # Synthesize OCSF files from IM, to verify what information is preserved.
    ocsf_gen = generate_ocsf(jadn_pkg)
    os.makedirs(gen_dir := os.path.join(output_dir, 'ocsf-generated'), exist_ok=True)
    # dump_ocsf(ocsf_gen, gen_dir)


if __name__ == '__main__':
    fire.Fire(create_im)
