#!/usr/bin/python3

from collections import defaultdict

def obj2wrl(obj_in, wrl_out):
    f = open(obj_in)
    out = open(wrl_out, "w")

    vertices = []
    faces = defaultdict(list)
    materials = {}

    use_mtl = 0
    new_mtl = None

    for line in f:
        line = line.strip("\r\n")
        if line.startswith("v "):
            line = line.strip("v ").strip("\n")
            vertices.append(tuple([float(x) for x in line.split(" ")]))
        elif line.startswith("usemtl"):
            use_mtl = line.split(" ")[1].strip("\n")
        elif line.startswith("f"):
            line = [x.strip("/\n") for x in line.split(" ")]
            faces[use_mtl].append((int(line[1])-1, int(line[2])-1, int(line[3])-1))
        elif line.startswith("newmtl"):
            new_mtl = line.split(" ")[1]
            materials[new_mtl] = {}
        elif line.startswith("Ka"):
            materials[new_mtl]["Ka"] = line.split("Ka ")[1]
        elif line.startswith("Kd"):
            materials[new_mtl]["Kd"] = line.split("Kd ")[1]
        elif line.startswith("Ks"):
            materials[new_mtl]["Ks"] = line.split("Ks ")[1]


    out.write("#VRML V2.0 utf8\n\n")

    for k,v in materials.items():

        out.write("""
        Shape {{
            appearance Appearance {{material DEF {name} Material {{
                ambientIntensity 0.271
                diffuseColor {diffuse}
                specularColor {specular}
                emissiveColor 0.0 0.0 0.0
                shininess 0.70
                transparency 0.0
                }}
            }}
        }}
        """.format(name="mat_"+k, diffuse=v["Kd"], specular=v["Ks"]))

    for mat in faces.keys():
        verts = []
        fcs = []
        indexes = {}

        for f in faces[mat]:
            face = list(f)
            for i, n in enumerate(face):
                if not face[i] in indexes:
                    verts.append(vertices[n])
                    indexes[n] = len(verts)-1
                face[i] = indexes[n]
            fcs.append(face)
        
        verts_str = ",".join(["{} {} {}".format(v[0], v[1], v[2]) for v in verts])
        faces_str = ",".join(["{},{},{},-1".format(f[0], f[1], f[2]) for f in fcs])
        #print(verts_str)

        out.write("""Shape { geometry IndexedFaceSet 
        { creaseAngle 0.50 coordIndex [""")
        out.write(faces_str)
        out.write("]\n")
        out.write("coord Coordinate { point [\n")
        out.write(verts_str)
        out.write("] }}\n")
        out.write("appearance Appearance{{material USE mat_{} }}".format(mat))
        out.write("}")
        out.write("\n\n")

    out.close()
    print("{} written".format(wrl_out))

import sys
if __name__ == "__main__":
    obj2wrl(sys.argv[1], sys.argv[2])