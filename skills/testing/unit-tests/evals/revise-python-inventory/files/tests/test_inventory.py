import time
from unittest import mock

import pytest

from inventory import Inventory, OutOfStock, UnknownReservation

inv = Inventory(hold_seconds=1)


def test1():
    inv.add("apple", 5)
    assert inv._items["apple"] == 5
    inv.add("apple", 3)
    assert inv._items["apple"] == 8
    with pytest.raises(ValueError):
        inv.add("apple", 0)
    with pytest.raises(ValueError):
        inv.add("apple", -2)


def test2():
    # depends on test1 having added apples
    h = inv.reserve("apple", 3)
    assert inv.available("apple") == 5
    inv.commit(h)
    assert inv._items["apple"] == 5


def test_reserve_too_many():
    inv.add("pear", 1)
    try:
        inv.reserve("pear", 2)
        assert False
    except OutOfStock:
        pass


def test_hold_expires():
    inv.add("plum", 2)
    h = inv.reserve("plum", 2)
    assert inv.available("plum") == 0
    time.sleep(1.1)
    assert inv.available("plum") == 2
    with pytest.raises(UnknownReservation):
        inv.commit(h)


def test_release():
    inv.add("kiwi", 4)
    with mock.patch.object(inv, "_record") as rec:
        h = inv.reserve("kiwi", 4)
        inv.release(h)
        assert rec.call_count == 2
    assert inv.available("kiwi") == 4
    with pytest.raises(UnknownReservation):
        inv.release(h)
