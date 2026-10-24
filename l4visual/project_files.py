"""Project folder operations; the v1 .l4vp schema stays unchanged.
Folders are metadata in project.library and file paths stay relative to scripts/vscripts.
"""

def norm_path(value):
    text=str(value).replace('\\','/').strip('/')
    parts=text.split('/') if text else []
    if any(part in ('','.','..') for part in parts):raise ValueError('无效的相对路径')
    return '/'.join(parts)

def parent_folder(path):
    text=norm_path(path)
    return text.rsplit('/',1)[0] if '/' in text else ''

def folder_set(project):
    return project.library.setdefault('project_folders',[])

def list_folders(project):
    result=set(folder_set(project))
    for document in project.documents:
        path=parent_folder(document.name)
        while path:
            result.add(path);path=parent_folder(path)
    expanded=set()
    for folder in result:
        while folder:
            expanded.add(folder);folder=parent_folder(folder)
    return expanded

def rename_prefix(project,old,new):
    old=norm_path(old);new=norm_path(new)
    if not old or not new or new.startswith(old+'/'):raise ValueError('目录移动会造成循环')
    def sub(path):return new+path[len(old):] if path==old or path.startswith(old+'/') else path
    folders=folder_set(project);folders[:]=sorted({sub(x) for x in folders})
    renames={d.name:sub(d.name) for d in project.documents}
    for document in project.documents:
        document.name=renames[document.name]
        document.includes=[renames.get(dep,dep) for dep in document.includes]

def remove_prefix(project,path):
    path=norm_path(path)
    if not path:raise ValueError('根目录不可删除')
    dead={d.name for d in project.documents if d.name.startswith(path+'/')}
    project.documents[:]=[d for d in project.documents if d.name not in dead]
    for d in project.documents:d.includes=[ref for ref in d.includes if ref not in dead]
    folders=folder_set(project);folders[:]=[f for f in folders if f!=path and not f.startswith(path+'/')]
