import os
import glob
from fnmatch import fnmatch
import re
import javalang as jl
from pathlib import Path
import csv



pattern = '*.java'
log_pattern = r'LOGGER\.[a-z]+[(][^;]+;'
log_statement = []
src_path = 'Refs\\elasticsearch-master\\elasticsearch-master'
cwd = os.getcwd()
mypath = cwd + "\\elasticsearch-master"
csv_columns = ["method_name", "level", "static_variavles", "dynamic_variavles"]
csv_file = input("Enter output file name: ") + ".csv"
out_file = open(csv_file, "a", newline='', encoding="utf8")
writer = csv.writer(out_file)
writer.writerow(csv_columns)


def __get_start_end_for_node(node_to_find):
    start = None
    end = None
    for path, node in tree:
        if start is not None and node_to_find not in path:
            end = node.position
            return start, end
        if start is None and node == node_to_find:
            start = node.position
    return start, end



def __get_string(start, end):
    if start is None:
        return ""

    # positions are all offset by 1. e.g. first line -> lines[0], start.line = 1
    end_pos = None

    if end is not None:
        end_pos = end.line - 1

    lines = data.splitlines(True)
    string = "".join(lines[start.line:end_pos])
    string = lines[start.line - 1] + string

    # When the method is the last one, it will contain a additional brace
    if end is None:
        left = string.count("{")
        right = string.count("}")
        if right - left == 1:
            p = string.rfind("}")
            string = string[:p]

    return string



for path, subdirs, files in os.walk(mypath):
    for name in files:
        filepath = os.path.join(path, name)
        if filepath.endswith('.java'):

            data = open(filepath, encoding="utf8").read()
            try:
                tree = jl.parse.parse(data)
                methods = {}
                for _, node in tree.filter(jl.tree.MethodDeclaration):
                    start, end = __get_start_end_for_node(node)
                    methods[node.name] = __get_string(start, end)

                log_statement = []

                for (function_name, function_body) in methods.items():
                    logs = re.findall(log_pattern, function_body, re.IGNORECASE)
                    for log in logs:
                        new_item = {}
                        new_item['method_name'] = function_name
                        logtree = list(jl.tokenizer.tokenize(log))
                        node_len = len(logtree)
                        new_item['level'] = logtree[2].value
                        new_item['static_variavles'] = []
                        new_item['dynamic_variavles'] = []
                        for i in range(3, node_len, 1):
                            #             print(type(tree[i]), tree[i].value)
                            if type(logtree[i]) is jl.tokenizer.String:
                                new_item['static_variavles'].append(logtree[i].value)
                            if type(logtree[i]) is jl.tokenizer.Identifier:
                                new_item['dynamic_variavles'].append(logtree[i].value)
                        writer.writerow([new_item['method_name'], new_item['level'], new_item['static_variavles'], new_item["dynamic_variavles"]])
            except Exception:
                print(filepath)
                pass

out_file.close()

