import pkg_resources

def get_path(path):
    assert 'data' in path, '/data/ should be the first thing in the path'
    assert '.' in path, 'missing suffix, e.g. .png'

    pkg_path = pkg_resources.resource_filename('unstable', path)
    return pkg_path