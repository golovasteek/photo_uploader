import uploader


def test_isimage():
    assert uploader.isimage('test_data/IMG_8076.JPG')
    assert not uploader.isimage('test_data/test.txt')
