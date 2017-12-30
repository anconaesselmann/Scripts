#!/usr/bin/swift

import Foundation

enum EntryType {
    case folder
    case file
}

class XcodeEntry {
    let name: String
    let parent: String
    let id: String
    let id2: String
    
    let type: EntryType
    
    init(name: String, parent: String, type: EntryType = .folder) {
        self.name = name
        self.parent = parent
        self.type = type
        id = XcodeEntry.generateId()
        id2 = XcodeEntry.generateId()
    }
    
    private static func generateId() -> String {
        let uuid = UUID().uuidString
        let index1 = uuid.index(uuid.startIndex, offsetBy: 8)
        let index2 = uuid.index(index1, offsetBy: 1)
        let index3 = uuid.index(index2, offsetBy: 4)
        let index4 = uuid.index(index1, offsetBy: 16)
        let range = index2..<index3
        return String(uuid[..<index1]) + String(uuid[range]) + String(uuid[index4...])
    }
}

// MARK: - Files and directories

let encoding: String.Encoding = .utf8

let fm = FileManager.default

let path = URL(fileURLWithPath: fm.currentDirectoryPath)
let projectName = path.lastPathComponent
let xcodeProjectUrl = path.appendingPathComponent("\(projectName).xcodeproj/project.pbxproj")
let tempXcodeProjectUrl = path.appendingPathComponent("\(projectName).xcodeproj/_project.pbxproj")

let newEntry: XcodeEntry

if CommandLine.arguments.count > 2 {
    let parentFolderName: String
    switch CommandLine.arguments[1] {
    case "folder":
        let folderName = CommandLine.arguments[2]
        parentFolderName = CommandLine.arguments.count > 3 ? CommandLine.arguments[3] : projectName
        
        newEntry = XcodeEntry(name: folderName, parent: parentFolderName, type: .folder)
        print("Creating folder `\(folderName)` in `\(parentFolderName)`")
    default:
        let fileName = CommandLine.arguments[1]
        parentFolderName = CommandLine.arguments.count > 2 ? CommandLine.arguments[2] : projectName
        
        newEntry = XcodeEntry(name: fileName, parent: parentFolderName, type: .file)
        print("Creating file `\(fileName)` in `\(parentFolderName)`")
    }
} else if CommandLine.arguments.count == 2 {
    let fileName = CommandLine.arguments[1]
    
    newEntry = XcodeEntry(name: fileName, parent: projectName, type: .file)
    print("Creating file `\(fileName)` in `\(projectName)`")
} else {
    print("Not enough arguments")
    exit(-1)
}

guard
    let xcodeProjectFileHandle = try? FileHandle(forReadingFrom: xcodeProjectUrl),
    FileManager.default.createFile(atPath: tempXcodeProjectUrl.relativePath, contents: nil, attributes: nil),
    let tempXcodeProjectFileHandle = try? FileHandle(forWritingTo: tempXcodeProjectUrl),
    let delimData  = "\n".data(using: encoding)
else {
    exit(-1)
}
var chunkSize = 4096
var buffer = Data(capacity: chunkSize)
var atEof = false

func readLine() -> String? {
    while !atEof {
        if let range = buffer.range(of: delimData) {
            let line = String(data: buffer.subdata(in: 0..<range.lowerBound), encoding: encoding)
            buffer.removeSubrange(0..<range.upperBound)
            return line
        }
        let tmpData = xcodeProjectFileHandle.readData(ofLength: chunkSize)
        if tmpData.count > 0 {
            buffer.append(tmpData)
        } else {
            atEof = true
            if buffer.count > 0 {
                let line = String(data: buffer as Data, encoding: encoding)
                buffer.count = 0
                return line
            }
        }
    }
    return nil
}

enum XcodeSection {
    case pbxGroup
    case pbxSourcesBuildPhase
    case none
}

var xcodeSection: XcodeSection = .none

var matchingConditions = 0

struct Strings {
    static let projectEntry = "\t\t\t\t%@ /* %@ */,\n"
    static let folderDefinition = "\t\t%@ /* %@ */ = {\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n\t\t\t);\n\t\t\tname = %@;\n\t\t\tsourceTree = \"<group>\";\n\t\t};\n"
    static let pbxBuildFileEntry = "\t\t%@ /* %@ in Sources */ = {isa = PBXBuildFile; fileRef = %@ /* %@ */; };\n"
    static let gpbxFileReferenceEnry = "\t\t%@ /* %@ */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = %@; path = %@; sourceTree = \"<group>\"; };\n"
    static let pbxSourcesBuildPhase = "\t\t\t\t%@ /* %@ in Sources */,\n"
    static let headerFileExtension = ".h"
    static let implementationFileExtension = ".m"
    static let swiftFileExtension = ".swift"
    static let endPbxBuildFileSection = "/* End PBXBuildFile section */"
    static let endPbxFileReferenceSection = "/* End PBXFileReference section */"
    static let beginPbxGroupSection = "/* Begin PBXGroup section */"
    static let endPbxGroupSection = "/* End PBXGroup section */"
    static let beginPbxSourceBuildPhaseSection = "/* Begin PBXSourcesBuildPhase section */"
}

func getProjectEntry(for xCodeEntry: XcodeEntry) -> String {
    let id: String
    switch xCodeEntry.type {
    case .folder: id = xCodeEntry.id
    case .file: id = xCodeEntry.id2
    }
    return String(format: Strings.projectEntry, id, xCodeEntry.name)
}

func getFolderDefinition(for xCodeEntry: XcodeEntry) -> String {
    return String(format: Strings.folderDefinition, xCodeEntry.id, xCodeEntry.name, xCodeEntry.name)
}

func getPbxBuildFileEntry(for xCodeEntry: XcodeEntry) -> String? {
    guard !xCodeEntry.name.hasSuffix(Strings.headerFileExtension) else { print("Error, header files should not have a PBXBuildFileEntry"); exit(-1) }
    return String(format: Strings.pbxBuildFileEntry, xCodeEntry.id, xCodeEntry.name, xCodeEntry.id2, xCodeEntry.name)
}

func getPbxFileReferenceEnry(for xCodeEntry: XcodeEntry) -> String {
    let fileType: String
    if xCodeEntry.name.hasSuffix(Strings.swiftFileExtension) {
        fileType = "sourcecode.swift"
    } else if xCodeEntry.name.hasSuffix(Strings.headerFileExtension) {
        fileType = "sourcecode.c.h"
    } else if xCodeEntry.name.hasSuffix(Strings.implementationFileExtension) {
        fileType = "sourcecode.c.objc"
    } else {
        print("Error, \(xCodeEntry.name) has an unsupported file type.")
        exit(-1)
    }
    return String(format: Strings.gpbxFileReferenceEnry, xCodeEntry.id2, xCodeEntry.name, fileType, xCodeEntry.name)
}

func getPbxSourcesBuildPhase(for xCodeEntry: XcodeEntry) -> String? {
    guard !xCodeEntry.name.hasSuffix(".h") else {
        return nil
    }
    return String(format: Strings.pbxSourcesBuildPhase, xCodeEntry.id, xCodeEntry.name)
}

while let line = readLine() {
    defer {
        tempXcodeProjectFileHandle.write((line + "\n").data(using: encoding)!)
    }

    switch line {
    case Strings.endPbxBuildFileSection:
        if newEntry.type == .file {
            if let pbxBuildFileEntry = getPbxBuildFileEntry(for: newEntry) {
                tempXcodeProjectFileHandle.write((pbxBuildFileEntry).data(using: encoding)!)
            }
        }
    case Strings.endPbxFileReferenceSection:
        if newEntry.type == .file {
            let pbxFileReferenceEnry = getPbxFileReferenceEnry(for: newEntry)
            tempXcodeProjectFileHandle.write((pbxFileReferenceEnry).data(using: encoding)!)
        }
    case Strings.beginPbxGroupSection:
        xcodeSection = .pbxGroup
    case Strings.endPbxGroupSection:
        if newEntry.type == .folder {
            let folderDefinition = getFolderDefinition(for: newEntry)
            tempXcodeProjectFileHandle.write((folderDefinition).data(using: encoding)!)
        }
        xcodeSection = .none
    case Strings.beginPbxSourceBuildPhaseSection:
        xcodeSection = .pbxSourcesBuildPhase
    default: ()
    }


    switch xcodeSection {
    case .pbxGroup:
        if line.hasSuffix("/* \(newEntry.parent) */ = {") {
            matchingConditions += 1
        } else if matchingConditions > 0 && line.hasSuffix("children = (") {
            matchingConditions += 1
        } else if matchingConditions == 2 {
            let folderEntry = getProjectEntry(for: newEntry)
            tempXcodeProjectFileHandle.write((folderEntry).data(using: encoding)!)
            matchingConditions = 0
        }
    case .pbxSourcesBuildPhase:
        if line.hasSuffix("files = (") {
            matchingConditions += 1
        } else if matchingConditions > 0 {
            if newEntry.type == .file {
                if let sourceBuildPhase = getPbxSourcesBuildPhase(for: newEntry) {
                    tempXcodeProjectFileHandle.write((sourceBuildPhase).data(using: encoding)!)
                }
            }
            matchingConditions = 0
            xcodeSection = .none
        }
    default: ()
    }
}

tempXcodeProjectFileHandle.closeFile()
tempXcodeProjectFileHandle.closeFile()

do {
    try FileManager.default.removeItem(at: xcodeProjectUrl)
    let _ = try FileManager.default.replaceItemAt(xcodeProjectUrl, withItemAt: tempXcodeProjectUrl, backupItemName: nil, options: [])
} catch {
    print("Xcode project file could not be modified")
    exit(-1)
}

exit(0)
