# PersonWsiData.py

''' dataframe for one person's wsi data '''

class PersonWsiData():
    def __init__(self, wsiImage):
        self._wsiImage = wsiImage
        self._imageSections = [ ]

    # appends an ImageSection to the _imageSection list
    def appendImageSection(self, imageSection):
        self._imageSections.append(imageSection)
