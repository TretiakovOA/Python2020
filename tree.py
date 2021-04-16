import os
import pathlib
import stat
import time
import typing as tp
import binascii

from pyvcs.repo import create_git_path
from pyvcs.index import GitIndexEntry, read_index
from pyvcs.objects import hash_object, find_object
from pyvcs.refs import get_ref, is_detached, resolve_head, update_ref

def write_tree(gitdir: pathlib.Path, index: tp.List[GitIndexEntry], dirname: str = "") -> str:
    # PUT YOUR CODE HERE
    if "GIT_DIR" not in os.environ:
        os.environ["GIT_DIR"] = ".git"    
    last_dir = None
    current_dir = dirname
    content = b""  
    for entry in index:             
        current_name = os.path.relpath(entry.name, dirname)        
        if "/" in current_name:            
            left_slash = current_name.find("/")
            last_dir = current_dir
            current_dir = os.path.join(dirname, current_name[:left_slash])
            if last_dir != current_dir:
                entries_to_tree = []
                for possible_entry in index:
                    if possible_entry.name.startswith(current_dir):
                        entries_to_tree.append(possible_entry)
                inner_tree = write_tree(gitdir, entries_to_tree, current_dir)
                content += f"40000 {current_dir}\x00".encode("ascii")
                content += binascii.unhexlify(inner_tree)
        else:
            content += f"100644 {current_name}\x00".encode("ascii")  
            content += entry.sha1 
    tree = hash_object(content ,"tree", True)      
    return tree
    

def commit_tree(
    gitdir: pathlib.Path,
    tree: str,
    message: str,
    parent: tp.Optional[str] = None,
    author: tp.Optional[str] = None,
) -> str:
    # PUT YOUR CODE HERE
    if "GIT_DIR" not in os.environ:
        os.environ["GIT_DIR"] = ".git" 
    if author is None:
        author = f"{os.environ['GIT_AUTHOR_NAME']} <{os.environ['GIT_AUTHOR_EMAIL']}>"
    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = "{} {}{:02}{:02}".format(
        timestamp,
        "+" if utc_offset > 0 else "-",
        abs(utc_offset) // 3600,
        (abs(utc_offset) // 60) % 60,
    )
    content = f"tree {tree}\n"
    if parent:
        content += f"parent {parent}\n"
    content += f"author {author} {author_time}\ncommitter {author} {author_time}\n\n{message}\n"
    
    sha = hash_object(content.encode("ascii"), "commit", True)
    return sha
