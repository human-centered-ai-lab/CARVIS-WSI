# PersonWsiData.py

''' dataframe for one person's wsi data '''

class PersonWsiData():
    def __init__(self, wsi):
        self._wsi = wsi
        self._imageSections = [ ]

    # appends an ImageSection to the _imageSection list
    def appendImageSections(self, imageSection):
        self._imageSections = imageSection.copy()
