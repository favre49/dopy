from PyQt4 import QtGui, QtCore
import sys, os, re, shutil, csv, sqlite3
from PIL import Image
import hashlib, random, base64, uuid
import niggerFiles

def generateDatabase():
        csvFilePath = QtGui.QFileDialog.getOpenFileName(None, "Locate the Student Details csv file", "", "*.csv")
        if csvFilePath == "": return None #FileDialog closed
        try:
            databaseFilePath = os.getcwd() + os.sep + "resources" + os.sep +"database.db"
            database = sqlite3.connect(databaseFilePath)
            cursor = database.cursor()
            csvfile = open(csvFilePath, "r")
            try:
                cursor.execute("drop table if exists studrec")
                cursor.execute('''create table studrec
                         (REC text, IDNO text, NAME text,
                          GENDER text, HOSCODE text, ROOMNO text)''')
                cursor.execute('''create table nicks
                         (NICK text PRIMARY KEY, IDNO text)''')
                cursor.execute('''create table passwords
                         (TASK text, password text)''')
                password = "0000"
                cursor.execute("insert into passwords values(?,?)", ("UNBILLING",hashPassword(password))) #0000
                cursor.execute("insert into passwords values(?,?)", ("EMAILING",password)) #0000
            except Exception as e:
                print("error creating tables:", str(e))
                pass
            reader = csv.reader(csvfile)
            for i, row in enumerate(reader):
                if i == 0: continue
                if row[1][-1].upper() == "P":
                        row1 = row[1][:-1]
                        print(row1)
                else:
                        row1 = row[1]

                cursor.execute("insert into studrec values(?,?,?,?,?,?)", (row[0], row1.upper(), row[2].upper(), row[3].upper(), row[4].upper(), row[5]))
            database.commit()
            csvfile.close()
            QtGui.QMessageBox.information(None, "Sucsex!!!", "The Database has been generated successfully!!!", QtGui.QMessageBox.Ok)

        except Exception as e:
            print("error populating database", str(e))
            QtGui.QMessageBox.information(None, "Fayul!!!", "Database Not happening", QtGui.QMessageBox.Ok)


def hashPassword(password):

    salt = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    t_sha = hashlib.sha512()
    t_sha.update(password.encode()+salt)
    return '{}${}'.format(base64.urlsafe_b64encode(t_sha.digest()).decode(),salt.decode())

def isValidPassword(password, hashedPassword):
    salt = hashedPassword.split("$")[-1].encode()
    t_sha = hashlib.sha512()
    t_sha.update(password.encode()+salt)
    if hashedPassword == '{}${}'.format(base64.urlsafe_b64encode(t_sha.digest()).decode(),salt.decode()):
        return True
    else:
        return False

def rename(self, path):
        folderName = path.split(os.sep)[-1]
        if re.match(r'[0-9]+[rR]', folderName):
            files = os.listdir(path)
            self.setEnabled(False)
            done = 0
            failed = 0
            for i, file_ in enumerate(files):
                try:
                    before = path + os.sep + file_
                    extension = file_.split(".")[-1]
                    after = path + os.sep + folderName.upper() + str(i+1).zfill(2)
                    if extension: after += "." + extension
                    os.rename(before, after)
                    done += 1
                except:
                    failed += 1
                    pass
            QtGui.QMessageBox.information(self, "Snaps Renamed!!!", "Snaps successfully renamed:\t\t{}\nSnaps failed:\t\t{}".format(done,failed), QtGui.QMessageBox.Ok)
        else:
            QtGui.QMessageBox.information(self, "Snaps not Renamed!!!", "The Snaps have not been renamed", QtGui.QMessageBox.Ok)
        self.setEnabled(True)

#copy roll, outsi and dept snaps to respective folders after resizing them

def readSnaps(path):

    folders = os.listdir(path)
    print(path)
    dataList = [] #[snapName, folderName, idNo, copies, newCopies = oldCopies, path]
    for folder in folders:
        print("folder: " + folder)
        folderName = folder
        snaps = os.listdir(path + os.sep + folderName)
        for snap in snaps:
            print("\tsnap :" + snap)
            snapWithoutExt = "".join(snap.split('.')[:-1]) if len(snap.split('.')) > 1 else snap
            rec = snapWithoutExt.split('_')
            if len(rec) != 5:
                print(rec)
                print("errrror")
                return None
            idNo = rec[4]
            snapName = rec[2]
            snapPath = path + os.sep + folderName + os.sep + snap
            #print("this", (snapName, idNo), [list_ for list_ in dataList])
            try:
                i = [(list_[0],list_[2]) for list_ in dataList].index((snapName, idNo))
                dataList[i][3] += 1
                dataList[i][4] += 1
            except:
                dataList.append([snapName, folderName, idNo, 1, 1, snapPath])

    return dataList

def generateBill(billingList, database):
    print("Generating BILL")
    list_ = database.cursor.execute("select * from studrec")

    finalBill = []
    list_2 = []
    sum_ = 0
    for rec in list_:
        #print(rec[1])
        numSnaps = 0
        #print(database.idValid(rec[1]))
        id = database.idValid(rec[1])[0]
        for i,entry in enumerate(billingList):
            if entry[2] == id:
                #print(entry[4])
                list_2.append(i)
                numSnaps += entry[4]
                sum_ += entry[4]
        finalBill.append((rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], numSnaps))
    csvfile = open('suBILL.csv', 'w', newline='')
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(["REC", "IDNO", "NAME", "GENDER", "HOSCODE", "ROOMNO", "SNAPS"])
    for rec in finalBill:
        writer.writerow(rec)
    csvfile.close()
    print(len(list_2), sum_)
    for x in list_2:
        if list_2.count(x)>1:
                print(billingList[x])
    reply = QtGui.QMessageBox.question(None, 'View File',
            "The bill has been generated.\nWanna check it out?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
            QtGui.QMessageBox.No)
    if reply == QtGui.QMessageBox.Yes:
            os.startfile('suBILL.csv')
    else:
        return None



def resizeAndSave(billingWidget):
    #def function():
        #print("just inside")
        roll = billingWidget.roll
        database = billingWidget.database
        FIXED_EDGE = 1024 #Fixed longer edge of snap
        rollName = roll.name.split(os.sep)[-1]
        sourcePath = roll.path

        #for an empty roll, do not proceed
        if not roll.snapList:
            QtGui.QMessageBox.information(None, "Message", "There are no snaps to bill", QtGui.QMessageBox.Ok)
            return None

        #handling destinationpath
        trackedPathFile = open(os.getcwd() + os.sep + "resources" + os.sep
                               + "trackedPath.txt", "r")
        openFolder = os.path.expanduser('~')
        for line in trackedPathFile: openFolder = os.sep.join(line.split(os.sep)[:-1])
        print("patha", openFolder)
        destinationPath = QtGui.QFileDialog.getExistingDirectory(None,"Locate the Billed Snaps Folder", openFolder)
        if destinationPath == "": return None
        trackedPathFile.close()


        progress = niggerFiles.customProgressWidget1()
        progress.headerLabel.setText("Resizing and Copying Snaps")
        #count total no of copies to be made
        totalCount = 0
        for snap in roll.snapList:
            if snap.dept: totalCount += 1
            if snap.outsi: totalCount += snap.outsi
            for entry in snap.idList: totalCount += entry[2]
        progress.bar.setRange(0,totalCount)
        progress.messageLabel.setText("copying {} of {} snaps".format(1,totalCount))
        progress.bar.setValue(1)
        progress.show()
        billingWidget.setEnabled(False)

        billingPath = os.path.join(destinationPath, rollName)
        print(billingPath)
        deptPath = os.sep.join(destinationPath.split(os.sep)[:-1]) + os.sep + "Departments"
        outsiPath = os.sep.join(destinationPath.split(os.sep)[:-1]) + os.sep + "Outsi"

        #Create roll folder
        try:
            os.mkdir(billingPath)
        except: #if folder has already been billed
            reply = QtGui.QMessageBox.question(None, 'Message',
                                               "This Folder has already been billed. Do you want\nto go ahead and overwrite the files?",
                                               QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.No: #Terminate
                return None
            else: #Delete existing folder, create new one
                shutil.rmtree(billingPath)
                os.mkdir(billingPath)

        #variables to count total no of snaps copied
        rollCount = 0
        deptCount = 0
        outsiCount = 0
        emailCount = 0
        failedResize = 0
        failedCopies = 0

        #print(roll.snapList)
        for snap in roll.snapList:
            #print("hi")
            #Extract name and extension of files with and without extensions
            snapExtension = snap.name.split('.')[-1] if len(snap.name.split('.')) > 1 else ""
            snapName = "".join(snap.name.split('.')[:-1]) if len(snap.name.split('.')) > 1 else snap.name

            infile = open(sourcePath + os.sep + snap.name, 'rb')
            unsupportedFormat = False

            # #handling unknown formats
            # unsupportedFormat = False
            # try:
            #     #Resize the snap
            #     im = Image.open(infile)
            #     width, height = im.size
            #     size = (FIXED_EDGE, FIXED_EDGE * height / width) if width > height else (FIXED_EDGE * width / height, FIXED_EDGE)
            #     im.thumbnail(size, Image.ANTIALIAS)
            #     im.save(sourcePath+os.sep+snap.name, quality=95)
            # except Exception as e:
            #     print(e)
            #     failedResize += 1
            #     unsupportedFormat = True

            #     continue

            #Copy roll snaps
            im = Image.open(infile)
            idList = snap.idList
            #print("idlist", idList)
            for entry in idList:
                id = entry[1]
                numCopies = entry[2]
                student = database.idValid(id)
                roomDetails = student[4] + "_" + student[5]

                for copyNo in range(numCopies):
                    try:
                        print("check0045", snapExtension, snapName)
                        if snapExtension: outfile = open(billingPath+os.sep+"{}_{}_{}_{}.{}".format(roomDetails,snapName,copyNo + 1,id,snapExtension), 'wb')
                        else: outfile = open(billingPath+os.sep+"{}_{}_{}_{}".format(roomDetails,snapName,copyNo+1,id), 'wb')
                        if not unsupportedFormat: im.save(outfile, quality = 95) #save resized snap
                        else: #copying without resizing
                            bufferSize = 100000
                            buffer = infile.read(buffersize)
                            while len(buffer):
                                outfile.write(buffer)
                                buffer = infile.read(buffersize)
                        outfile.close()
                        rollCount += 1
                    except:
                        failedCopies += 1

                    progress.messageLabel.setText("copying {} of {} snaps".format(progress.bar.value()+1,totalCount))
                    progress.bar.setValue(progress.bar.value()+1)

            #Copy dept snaps
            if snap.dept:
                #create path if it doesnt exist
                try:
                    os.mkdir(deptPath)
                    os.mkdir(deptPath+os.sep+"{}".format(snap.dept))
                except:
                    try:
                        os.mkdir(deptPath+os.sep+"{}".format(snap.dept))
                    except:
                        pass
                if snapExtension: outfile = open(deptPath+os.sep+"{}"+os.sep+"{}.{}".format(snap.dept,snapName,snapExtension), 'wb')
                else:
                    outfile = open(deptPath+os.sep+"{}"+os.sep+"{}".format(snap.dept,snapName), 'wb')
                try:
                    if not unsupportedFormat: im.save(outfile, quality=95) #save resized snap
                    else: #copying without resizing
                        bufferSize = 100000
                        buffer = infile.read(buffersize)
                        while len(buffer):
                            outfile.write(buffer)
                            buffer = infile.read(buffersize)
                    outfile.close()
                    deptCount += 1
                except:
                    failedCopies += 1


                progress.messageLabel.setText("copying {} of {} snaps".format(progress.bar.value()+1,totalCount))
                progress.bar.setValue(progress.bar.value()+1)

            #Copy outsi snaps
            if snap.outsi:
                #create path if it doesnt exist
                try:
                    os.mkdir(outsiPath)
                except:
                    pass
                quantity = snap.outsi
                for copyNo in range(quantity):
                    try:
                        if snapExtension: outfile = open(outsiPath+os.sep+"{}_{}.{}".format(snapName,copyNo + 1,snapExtension), 'wb')
                        else: outfile = open(outsiPath+os.sep+"{}_{}".format(snapName,copyNo + 1), 'wb')
                        if not unsupportedFormat: im.save(outfile, quality=95) #save resized snap
                        else: #copying without resizing
                            bufferSize = 100000
                            buffer = infile.read(buffersize)
                            while len(buffer):
                                outfile.write(buffer)
                                buffer = infile.read(buffersize)
                        outfile.close()
                        outsiCount += 1
                    except:
                        failedCopies += 1

                #Generate/update csv for outsi
                emailList = [entry[1] for entry in snap.emailList ]
                row = snapName + "_1." + snapExtension if snapExtension else snapName + "_1"
                row+=";"
                try:
                    csvFile = open(outsiPath + os.sep + "outsi.csv", 'a+')
                    #add emailIDs with status = 0 to a string
                    for emailID in emailList:
                        row += emailID + "|0|"
                    if row[-1] == "|": row = row[:-1]
                    row += '\n'
                    csvFile.write(row)
                    csvFile.close()
                    emailCount += len(emailList)
                except:
                    pass

                progress.messageLabel.setText("copying {} of {} snaps".format(progress.bar.value()+1,totalCount))
                progress.bar.setValue(progress.bar.value()+1)

            infile.close()

        progress.close()
        billingWidget.setEnabled(True)
        QtGui.QMessageBox.information(None, "Success!!!","Snaps copied successfully\nRoll Snaps copied:\t\t{}\nOutsi Snaps copied:\t\t{}\nDept Snaps Copied:\t\t{}\nEmailIDs written\t\t{}\nSnaps not resized\t\t{}\nSnaps not copied\t\t{}\nPlease make a note of it!!!".format(rollCount,outsiCount,deptCount,emailCount,failedResize,failedCopies), QtGui.QMessageBox.Ok)
        return 1

    #return function





#if __name__ == "__main__":
    #app = QtGui.QApplication(sys.argv)
    #generateDatabase()
    ##database = niggerFiles.Students("database.db")
    #p = niggerFiles.passwordWidget(database)
    #database.insertNick("ghattam", "11052")
    #database.insertNick("potTER", "11164")
    #database.clearAllNicks()
    #list_ = database.hostelValid("bd")
    #print(list_)
    #l = database.cursor.execute("select * from nicks")
    #for k in l: print(k)
    #n = addNickWidget()
    #app.exec_()
    #database.changePassword("unbilling", hashPassword("0000"))
    #password = database.getPassword("unbilling")
    #print("yes") if password == hashPassword("0000") else print("no")
    #hashedPassword = hashPassword("0000")
    #print(validPassword("0001", hashedPassword))
    #niggerFiles
