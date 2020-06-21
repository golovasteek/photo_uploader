import uploader
from datetime import date


def test_isimage():
    assert uploader.isimage('test_data/IMG_8076.JPG')
    assert not uploader.isimage('test_data/test.txt')


def test_shot_date():
    expected_date = date(2020, 5, 22)
    img_date = uploader.shot_date('test_data/IMG_8076.JPG')
    assert img_date.date() == expected_date
