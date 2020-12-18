from pyql import Object


def test_container_object_is_instance_of_object():
    MyObject = Object("MyObject", fields={"foo": str})

    obj = MyObject(foo="A")

    assert isinstance(obj, MyObject)
