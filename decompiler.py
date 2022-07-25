import zipfile
import subprocess
import shutil
import argparse
from pathlib import *

java_decompiler_path = "src/java-decompiler.jar"
jar_path = "ezjson.jar"
output_path = "result/"

def check_path():
    p = Path(java_decompiler_path)
    if p.is_file() == False:
        print("ERROR:\tdecompile tool is not exists")
        return False

    p1 = Path(jar_path)
    if p1.is_file() == False:
        print("ERROR:\tjar source is not exists")
        return False

    p2 = Path(output_path)
    if p2.is_dir() == False:
        print("ERROR:\toutput path is not exists")
        return False

    return True

def getJarName(jar_path):
    return jar_path.split("/")[-1]


#从jar反编译出java文件
def decompiler_jar():
    cmd_txt = "java -cp {} org.jetbrains.java.decompiler.main.decompiler.ConsoleDecompiler -dgs=true {} {}".format(java_decompiler_path,jar_path,output_path)
    _subProcess = subprocess.getstatusoutput(cmd_txt)

    if _subProcess[0] != 0:
        print(_subProcess[1])
    else:
        print(_subProcess[1])
        print("INFO:\tDecompiler class to java file successfully")

    with zipfile.ZipFile(Path(output_path).joinpath(getJarName(jar_path)),mode='r') as zfile:
        for file in zfile.namelist():
            zfile.extract(file,Path(output_path).joinpath(getJarName(jar_path).rstrip('.jar')+"_tmp"))

        Path(output_path).joinpath(getJarName(jar_path)).unlink()

# 根据反编译生成的文件，调整源码位置和依赖配置，生成一份项目源代码（可打包）
# maven项目
def gen():
    #copy demo to des
    demo = "src/maven_demo"
    res = Path("result/").joinpath(getJarName(jar_path).rstrip(".jar"))
    shutil.copytree(demo,res)

    src_path = Path(output_path).joinpath(getJarName(jar_path).rstrip('.jar')+"_tmp")
    src = src_path.joinpath("BOOT-INF/classes/com")
    des = res.joinpath("src/main/java/com")
    shutil.copytree(src,des)

    shutil.move(src_path.joinpath("BOOT-INF/classes/application.properties"),res.joinpath("src/main/resources/application.properties"))
    
    meta_inf_path = src_path.joinpath("META-INF/maven/")
    pom_path = ""

    for i in meta_inf_path.glob("**/*"):
        if "pom.xml" in str(i):
            pom_path = i

    if pom_path != "":
        shutil.move(pom_path,res.joinpath("pom.xml"))
        shutil.rmtree(src_path)
    else:
        print("pom.xml is not exists")

if __name__ == '__main__':
    
    epilog = r'''Example:
    python3 decompiler.py -jar ./ezjson.jar -o ./result/
    '''

    parse = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parse.add_argument('-jar', '--jar', help='jar包路径')
    parse.add_argument('-o', '--out', help='输入存放反编译后文件的目录')

    args = parse.parse_args()

    jar_path = args.jar
    output_path = args.out

    if jar_path is not None and output_path is not None:        
        decompiler_jar()
        gen()
    else:
        print("error parameters")