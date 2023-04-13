import pytest
from PyQt5 import QtCore
from pyopenva.efficient import Efficient


@pytest.fixture
def app(qtbot):
    test_efficient = Efficient()
    qtbot.addWidget(test_efficient)
    return test_efficient


def test_choose_insilico(app, qtbot):
    qtbot.mouseClick(app.btn_insilicova, QtCore.Qt.LeftButton)
    assert app.chosen_algorithm == "insilicova"
