debug = False

exec(open("../parameters/parameters.py").read())
exec(open("../code/path.py").read())
exec(open("../code/setupCPH.py").read())
exec(open("../code/functions.py").read())

if __name__ == '__main__':

    print("Running 01a.py")
    exec(open("01a.py").read())

    print("Running 01b.py")
    exec(open("01b.py").read())

    print("Running 01c.py")
    exec(open("01c.py").read())

    print("Running 01d.py")
    exec(open("01d.py").read())

    print("Running 02.py")
    exec(open("02.py").read())

