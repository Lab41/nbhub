import sys
import json
'''
take a file and unwrap the contents to a dictionary.
write the key=value terms out.

The program is intended to be caled from a bash
program to export the key=value pairs as environemnt
variables

'''


def main(argv):
    a = open(argv[0], 'r')
    b = a.readlines()[0].strip()
    data = json.loads(b)[0]

    for d in data.iterkeys():
        print "_docker_%s=%s" % (d.lower(), (str(data[d]).replace(' ', '')))


if __name__ == "__main__":
    main(sys.argv[1:])
