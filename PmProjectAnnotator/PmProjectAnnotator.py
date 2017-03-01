import ConfigParser
import csv
import xml.etree.ElementTree as ET


def getCommandDetail(pmHome):
    baseNumber = 7
    with open(pmHome + "/data/command_detail.ini", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        paramMap = {}

        for row in reader:
            count = 0
            paramList = []
            for item in row:
                commandType = row[0]
                index = count - baseNumber
                count += 1
                isParamItem = (index >= 0) and (index % 3) == 0 and (item != "")
                if isParamItem:
                    paramList.append(item)
            if len(commandType) > 0:
                paramMap[commandType] = paramList
    return paramMap


def getObjectDetail(pmHome):
    baseNumber = 6
    with open(pmHome + "/data/object_detail.ini", "r") as f:
        reader = csv.reader(f)
        header = next(reader)
        paramMap = {}

        for row in reader:
            objectType = row[0]
            objectName = row[2]
            count = 0

            paramList = [objectName]

            for item in row:
                index = count - baseNumber
                count += 1

                isParamItem = (index >= 0) and (index % 3) == 0 and (item != "")
                if isParamItem:
                    paramList.append(item)

            if len(objectType) > 0:
                paramMap[objectType] = paramList
    return paramMap


def convertXML(pmHome, protocolName, objectDetailMap, commandDetailMap, outputXmlFile):
    tree = ET.parse(pmHome + "/protocol/" + protocolName + "/project.prj")
    root = tree.getroot()
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xsi:noNamespaceSchemaLocation", "project.xsd")
    main = root.find("main")
    objectCount = 0

    for objectNode in main:
        objectCount +=1
        objectIdElement = ET.fromstring("<objectId>"+str(objectCount)+"</objectId>")
        objectNode.insert(0, objectIdElement)
        itemCount = 0

        for itemNode in objectNode:
            if itemNode.tag != "objectId":
                itemCount +=1
                itemIdElement = ET.fromstring("<itemId>"+str(itemCount)+"</itemId>")
                itemNode.insert(0, itemIdElement)

            objectTypeNode = itemNode.find("objectType")
            commandTypeNode = itemNode.find("commandType")

            if objectTypeNode != None:
                _processObjectTypeNode(itemNode, objectTypeNode, objectDetailMap)

            if commandTypeNode != None:
                _processCommandTypeNode(itemNode, commandTypeNode, commandDetailMap)

    tree.write(outputXmlFile, encoding="utf-8", xml_declaration=True)


def _processObjectTypeNode(itemNode, objectTypeNode, objectDetailMap):
    objectParamPrefix = "settingParam"
    objectTypeKey = objectTypeNode.text
    label = objectDetailMap.get(objectTypeKey)[0]

    objectTypeNode.set("name", label)

    count = 0
    for paramLabel in objectDetailMap.get(objectTypeKey):
        if count > 0:
            paramNode = itemNode.find(objectParamPrefix + str(count))
            if paramNode != None:
                paramNode.set("name", paramLabel)
        count += 1


def _processCommandTypeNode(itemNode, commandTypeNode, commandDetailMap):
    commandParamPrefix = "settingParam"
    key = commandTypeNode.text

    count = 1
    for paramLabel in commandDetailMap.get(key):
        paramNode = itemNode.find(commandParamPrefix + str(count))
        if paramNode != None:
            paramNode.set("name", paramLabel)
        count += 1


if __name__ == "__main__":
    config = ConfigParser.SafeConfigParser()
    config.read("../annotator.props")
    pmHome = config.get("ProtocolMakerProps", "ProtocolMakerHome")
    protocolName = config.get("ProtocolMakerProps", "ProtocolName")
    outputXmlFile = config.get("OutputProps", "OutputXmlDir") + "/" + config.get("OutputProps", "OutputXmlName")

    commandDetailMap = getCommandDetail(pmHome)
    objectDetailMap = getObjectDetail(pmHome)

    convertXML(pmHome, protocolName, objectDetailMap, commandDetailMap, outputXmlFile)
