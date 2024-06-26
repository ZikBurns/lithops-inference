from dso.client import Client
from jpype import *
from jpype import java
import lithopserve
import os

dso = os.environ.get('DSO')


def my_function(x):
    client = Client(dso)
    d = client.getAtomicCounter("cnt")
    return d.increment(x)


if __name__ == '__main__':
    fexec = lithopserve.FunctionExecutor(runtime='0track/lithopserve-dso:1.1')
    fexec.call_async(my_function, 3)
    client = Client(dso)
    c = client.getAtomicCounter("cnt")
    print("counter: " + str(c.tally()))
    print(fexec.get_result())
    print("counter: " + str(c.tally()))
