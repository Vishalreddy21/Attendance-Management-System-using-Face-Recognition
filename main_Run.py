import tkinter as tk
from tkinter import *
from tkinter import messagebox
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
from dotenv import load_dotenv
import subprocess
import pymysql.connections

# Load environment variables from .env file
load_dotenv()

# Get the base directory of the script
base_dir = os.path.dirname(os.path.abspath(__file__))

window = tk.Tk()
window.title("Attendance Management System using Face Recognition")
window.geometry('1280x720')
window.configure(background='grey80')

# Manual Attendance


def manually_fill():
    sb = tk.Toplevel(window)
    sb.title("Enter subject name...")
    sb.geometry('580x320')
    sb.configure(background='grey80')

    def err_screen_for_subject():
        def ec_delete():
            ec.destroy()
        ec = tk.Toplevel(sb)
        ec.geometry('300x100')
        ec.title('Warning!!')
        ec.configure(background='snow')
        Label(ec, text='Please enter your subject name!!!', fg='red',
              bg='white', font=('times', 16, ' bold ')).pack()
        Button(ec, text='OK', command=ec_delete, fg="black", bg="lawn green", width=9,
               height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

    def fill_attendance():
        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")

        subb = SUB_ENTRY.get()
        DB_table_name = str(subb + "_" + Date + "_Time_" +
                            Hour + "_" + Minute + "_" + Second)

        if subb == '':
            err_screen_for_subject()
            return

        try:
            connection = pymysql.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                db=os.getenv("MYSQL_DB")
            )
            cursor = connection.cursor()
            sql = f"CREATE TABLE IF NOT EXISTS `{DB_table_name}` (ID INT NOT NULL AUTO_INCREMENT, ENROLLMENT VARCHAR(100) NOT NULL, NAME VARCHAR(50) NOT NULL, DATE VARCHAR(20) NOT NULL, TIME VARCHAR(20) NOT NULL, PRIMARY KEY (ID));"
            cursor.execute(sql)
            connection.close()
        except Exception as e:
            messagebox.showerror(
                "Database Error", f"Failed to connect to database or create table: {e}", parent=sb)
            return

        sb.destroy()
        MFW = tk.Toplevel(window)
        MFW.title(f"Manually attendance of {subb}")
        MFW.geometry('880x470')
        MFW.configure(background='grey80')

        def err_screen1():
            errsc2 = tk.Toplevel(MFW)
            errsc2.geometry('330x100')
            errsc2.title('Warning!!')
            errsc2.configure(background='grey80')
            Label(errsc2, text='Please enter Student & Enrollment!!!',
                  fg='black', bg='white', font=('times', 16, ' bold ')).pack()

            def del_errsc2():
                errsc2.destroy()
            Button(errsc2, text='OK', command=del_errsc2, fg="black", bg="lawn green", width=9,
                   height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

        ENR = tk.Label(MFW, text="Enter Enrollment", width=15,
                       height=2, fg="black", bg="grey", font=('times', 15))
        ENR.place(x=30, y=100)

        STU_NAME = tk.Label(MFW, text="Enter Student name", width=15,
                            height=2, fg="black", bg="grey", font=('times', 15))
        STU_NAME.place(x=30, y=200)

        global ENR_ENTRY
        ENR_ENTRY = tk.Entry(MFW, width=20, validate='key',
                             bg="white", fg="black", font=('times', 23))
        ENR_ENTRY['validatecommand'] = (
            ENR_ENTRY.register(testVal), '%P', '%d')
        ENR_ENTRY.place(x=290, y=105)

        def remove_enr():
            ENR_ENTRY.delete(first=0, last=22)

        STUDENT_ENTRY = tk.Entry(
            MFW, width=20, bg="white", fg="black", font=('times', 23))
        STUDENT_ENTRY.place(x=290, y=205)

        def remove_student():
            STUDENT_ENTRY.delete(first=0, last=22)

        def enter_data_DB():
            ENROLLMENT = ENR_ENTRY.get()
            STUDENT = STUDENT_ENTRY.get()
            if ENROLLMENT == '' or STUDENT == '':
                err_screen1()
                return

            try:
                connection = pymysql.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    db=os.getenv("MYSQL_DB")
                )
                cursor = connection.cursor()
                time_str = datetime.datetime.fromtimestamp(
                    time.time()).strftime('%H:%M:%S')
                Insert_data = f"INSERT INTO `{DB_table_name}` (ID, ENROLLMENT, NAME, DATE, TIME) VALUES (0, %s, %s, %s, %s)"
                VALUES = (str(ENROLLMENT), str(STUDENT),
                          str(Date), str(time_str))
                cursor.execute(Insert_data, VALUES)
                connection.commit()
                connection.close()

                # These two lines have been removed to keep the data visible:
                # ENR_ENTRY.delete(first=0, last=22)
                # STUDENT_ENTRY.delete(first=0, last=22)

                messagebox.showinfo(
                    "Success", "Data entered successfully!", parent=MFW)
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to insert data: {e}", parent=MFW)

        def create_csv():
            try:
                connection = pymysql.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    db=os.getenv("MYSQL_DB")
                )
                cursor = connection.cursor()
                cursor.execute(f"SELECT * FROM `{DB_table_name}`;")

                results = cursor.fetchall()
                headers = [i[0] for i in cursor.description]
                connection.close()

                if not results:
                    messagebox.showinfo(
                        "Info", "No data has been entered for this session yet. Please use 'Enter Data' first.", parent=MFW)
                    return

                attendance_dir = os.path.join(base_dir, 'Attendance')
                manual_attendance_dir = os.path.join(
                    attendance_dir, 'Manually_Attendance')
                os.makedirs(manual_attendance_dir, exist_ok=True)

                csv_name = os.path.join(
                    manual_attendance_dir, f"Manually Attendance_{DB_table_name}.csv")

                with open(csv_name, "w", newline="") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(headers)
                    csv_writer.writerows(results)

                Notifi.configure(text="CSV created Successfully", bg="Green",
                                 fg="white", width=33, font=('times', 19, 'bold'))
                Notifi.place(x=180, y=380)

                root = tk.Toplevel(MFW)
                root.title(f"Attendance of {subb}")
                root.configure(background='grey80')
                with open(csv_name, newline="") as file:
                    reader = csv.reader(file)
                    for r_idx, col in enumerate(reader):
                        for c_idx, row in enumerate(col):
                            label = tk.Label(root, width=18, height=1, fg="black", font=(
                                'times', 13, ' bold '), bg="white", text=row, relief=tk.RIDGE)
                            label.grid(row=r_idx, column=c_idx)
            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to create CSV: {e}", parent=MFW)

        Notifi = tk.Label(MFW, text="", bg="Green", fg="white",
                          width=33, height=2, font=('times', 19, 'bold'))

        c1ear_enroll = tk.Button(MFW, text="Clear", command=remove_enr, fg="white", bg="black",
                                 width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
        c1ear_enroll.place(x=690, y=100)

        c1ear_student = tk.Button(MFW, text="Clear", command=remove_student, fg="white", bg="black",
                                  width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
        c1ear_student.place(x=690, y=200)

        DATA_SUB = tk.Button(MFW, text="Enter Data", command=enter_data_DB, fg="black", bg="SkyBlue1",
                             width=20, height=2, activebackground="white", font=('times', 15, ' bold '))
        DATA_SUB.place(x=170, y=300)

        MAKE_CSV = tk.Button(MFW, text="Convert to CSV", command=create_csv, fg="black", bg="SkyBlue1",
                             width=20, height=2, activebackground="white", font=('times', 15, ' bold '))
        MAKE_CSV.place(x=570, y=300)

        def attf():
            try:
                manual_attendance_dir = os.path.join(
                    base_dir, "Attendance", "Manually_Attendance")
                subprocess.Popen(f'explorer "{manual_attendance_dir}"')
            except FileNotFoundError:
                messagebox.showerror(
                    "Error", "File Explorer not found. This feature is for Windows only.", parent=MFW)

        attf_btn = tk.Button(MFW, text="Check Sheets", command=attf, fg="white", bg="black",
                             width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
        attf_btn.place(x=730, y=410)

    SUB = tk.Label(sb, text="Enter Subject : ", width=15, height=2,
                   fg="black", bg="grey80", font=('times', 15, ' bold '))
    SUB.place(x=30, y=100)

    global SUB_ENTRY
    SUB_ENTRY = tk.Entry(sb, width=20, bg="white",
                         fg="black", font=('times', 23))
    SUB_ENTRY.place(x=250, y=105)

    fill_manual_attendance = tk.Button(sb, text="Fill Attendance", command=fill_attendance, fg="black",
                                       bg="SkyBlue1", width=20, height=2, activebackground="white", font=('times', 15, ' bold '))
    fill_manual_attendance.place(x=250, y=160)


def clear():
    txt.delete(first=0, last=22)


def clear1():
    txt2.delete(first=0, last=22)


def err_screen():
    sc1 = tk.Toplevel(window)
    sc1.geometry('300x100')
    sc1.title('Warning!!')
    sc1.configure(background='grey80')
    Label(sc1, text='Enrollment & Name required!!!',
          fg='black', bg='white', font=('times', 16)).pack()

    def del_sc1():
        sc1.destroy()
    Button(sc1, text='OK', command=del_sc1, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)


def err_screen1():
    sc2 = tk.Toplevel(window)
    sc2.geometry('300x100')
    sc2.title('Warning!!')
    sc2.configure(background='grey80')
    Label(sc2, text='Please enter your subject name!!!',
          fg='black', bg="white", font=('times', 16)).pack()

    def del_sc2():
        sc2.destroy()
    Button(sc2, text='OK', command=del_sc2, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)


def take_img():
    l1 = txt.get()
    l2 = txt2.get()
    if not l1 or not l2:
        err_screen()
        return

    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cascades_path = os.path.join(
            base_dir, 'cascades', 'haarcascade_frontalface_default.xml')
        detector = cv2.CascadeClassifier(cascades_path)

        enrollment = txt.get()
        name = txt2.get()
        sampleNum = 0

        training_image_dir = os.path.join(base_dir, 'TrainingImage')
        os.makedirs(training_image_dir, exist_ok=True)

        while True:
            ret, img = cam.read()
            if not ret:
                messagebox.showerror(
                    "Camera Error", "Failed to capture image from webcam.")
                break

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sampleNum += 1
                img_path = os.path.join(
                    training_image_dir, f"{name}.{enrollment}.{sampleNum}.jpg")
                cv2.imwrite(img_path, gray[y:y+h, x:x+w])
                cv2.imshow('Frame', img)

            if cv2.waitKey(1) & 0xFF == ord('q') or sampleNum > 70:
                break

        cam.release()
        cv2.destroyAllWindows()

        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        Time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        row = [enrollment, name, Date, Time]

        student_details_dir = os.path.join(base_dir, 'StudentDetails')
        os.makedirs(student_details_dir, exist_ok=True)
        student_details_path = os.path.join(
            student_details_dir, 'StudentDetails.csv')

        file_exists = os.path.isfile(student_details_path)
        write_header = not file_exists or os.stat(
            student_details_path).st_size == 0

        with open(student_details_path, 'a+', newline='') as csvFile:
            writer = csv.writer(csvFile, delimiter=',')
            if write_header:
                writer.writerow(['Enrollment', 'Name', 'Date', 'Time'])
            writer.writerow(row)

        res = f"Images Saved for Enrollment: {enrollment}, Name: {name}"
        Notification.configure(text=res, bg="SpringGreen3",
                               width=50, font=('times', 18, 'bold'))
        Notification.place(x=250, y=400)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def subjectchoose():
    def Fillattendances():
        sub = tx.get()
        if not sub:
            err_screen1()
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            model_path = os.path.join(
                base_dir, 'TrainingImageLabel', 'Trainner.yml')
            recognizer.read(model_path)
        except Exception as e:
            Notifica.configure(
                text=f'Error: Model not found. Please train model.', bg="red", fg="black", width=33, font=('times', 15, 'bold'))
            Notifica.place(x=20, y=250)
            return

        harcascadePath = os.path.join(
            base_dir, 'cascades', 'haarcascade_frontalface_default.xml')
        faceCascade = cv2.CascadeClassifier(harcascadePath)

        student_details_path = os.path.join(
            base_dir, 'StudentDetails', 'StudentDetails.csv')
        if not os.path.exists(student_details_path):
            messagebox.showerror(
                "Error", "Student details CSV not found. Please add students first.")
            return

        df = pd.read_csv(student_details_path)
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        font = cv2.FONT_HERSHEY_SIMPLEX
        col_names = ['Enrollment', 'Name', 'Date', 'Time']
        attendance = pd.DataFrame(columns=col_names)

        now = time.time()
        future = now + 20

        while time.time() < future:
            ret, im = cam.read()
            if not ret:
                break
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)

            for (x, y, w, h) in faces:
                try:
                    enrollment_id, conf = recognizer.predict(
                        gray[y:y + h, x:x + w])

                    if conf < 70:
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(
                            ts).strftime('%Y-%m-%d')
                        timeStamp = datetime.datetime.fromtimestamp(
                            ts).strftime('%H:%M:%S')

                        name_series = df.loc[df['Enrollment']
                                             == enrollment_id, 'Name']
                        name = name_series.values[0] if not name_series.empty else 'Unknown'

                        tt = f"{enrollment_id}-{name}"
                        attendance.loc[len(attendance)] = [
                            enrollment_id, name, date, timeStamp]

                        cv2.rectangle(im, (x, y), (x + w, y + h),
                                      (0, 260, 0), 7)
                        cv2.putText(im, tt, (x + h, y), font,
                                    1, (255, 255, 0,), 4)
                    else:
                        tt = 'Unknown'
                        cv2.rectangle(im, (x, y), (x + w, y + h),
                                      (0, 25, 255), 7)
                        cv2.putText(im, tt, (x + h, y),
                                    font, 1, (0, 25, 255), 4)
                except Exception as e:
                    print(f"Prediction error: {e}")
                    continue

            attendance = attendance.drop_duplicates(
                ['Enrollment'], keep='first')
            cv2.imshow('Filling attendance...', im)
            if cv2.waitKey(1) & 0xff == 27:
                break

        cam.release()
        cv2.destroyAllWindows()

        if not attendance.empty:
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            timeStamp = datetime.datetime.fromtimestamp(
                ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStamp.split(":")

            attendance_dir = os.path.join(base_dir, 'Attendance')
            os.makedirs(attendance_dir, exist_ok=True)
            fileName = os.path.join(
                attendance_dir, f"{sub}_{date}_{Hour}-{Minute}-{Second}.csv")

            attendance.to_csv(fileName, index=False)

            DB_Table_name = f"{sub}_{date.replace('-', '_')}_Time_{Hour}_{Minute}_{Second}"
            try:
                connection = pymysql.connect(
                    host=os.getenv("MYSQL_HOST"),
                    user=os.getenv("MYSQL_USER"),
                    password=os.getenv("MYSQL_PASSWORD"),
                    db=os.getenv("MYSQL_DB")
                )
                cursor = connection.cursor()
                sql = f"CREATE TABLE IF NOT EXISTS `{DB_Table_name}` (ID INT NOT NULL AUTO_INCREMENT, ENROLLMENT VARCHAR(100) NOT NULL, NAME VARCHAR(50) NOT NULL, DATE VARCHAR(20) NOT NULL, TIME VARCHAR(20) NOT NULL, PRIMARY KEY (ID));"
                cursor.execute(sql)

                for index, row in attendance.iterrows():
                    insert_data = f"INSERT INTO `{DB_Table_name}` (ID, ENROLLMENT, NAME, DATE, TIME) VALUES (0, %s, %s, %s, %s)"
                    values = (str(row['Enrollment']), str(
                        row['Name']), str(row['Date']), str(row['Time']))
                    cursor.execute(insert_data, values)

                connection.commit()
                connection.close()
            except Exception as e:
                messagebox.showerror(
                    "Database Error", f"Failed to connect to database or create table: {e}")

            Notifica.configure(text='Attendance filled Successfully',
                               bg="Green", fg="white", width=33, font=('times', 15, 'bold'))
            Notifica.place(x=20, y=250)

            root = tk.Toplevel(windo)
            root.title(f"Attendance of {sub}")
            root.configure(background='grey80')
            with open(fileName, newline="") as file:
                reader = csv.reader(file)
                for r_idx, col in enumerate(reader):
                    for c_idx, row in enumerate(col):
                        label = tk.Label(root, width=10, height=1, fg="black", font=(
                            'times', 15, ' bold '), bg="white", text=row, relief=tk.RIDGE)
                        label.grid(row=r_idx, column=c_idx)
        else:
            Notifica.configure(text='No faces recognized.',
                               bg="Red", fg="white", width=33, font=('times', 15, 'bold'))
            Notifica.place(x=20, y=250)

    windo = tk.Toplevel(window)
    windo.title("Enter subject name...")
    windo.geometry('580x320')
    windo.configure(background='grey80')

    Notifica = tk.Label(windo, text="", bg="Green", fg="white",
                        width=33, height=2, font=('times', 15, 'bold'))

    def Attf():
        try:
            subprocess.Popen(
                f'explorer "{os.path.join(base_dir, "Attendance")}"')
        except FileNotFoundError:
            messagebox.showerror(
                "Error", "File Explorer not found. This feature is for Windows only.")

    attf_btn = tk.Button(windo, text="Check Sheets", command=Attf, fg="white", bg="black",
                         width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
    attf_btn.place(x=430, y=255)

    sub = tk.Label(windo, text="Enter Subject : ", width=15, height=2,
                   fg="black", bg="grey", font=('times', 15, ' bold '))
    sub.place(x=30, y=100)

    tx = tk.Entry(windo, width=20, bg="white", fg="black", font=('times', 23))
    tx.place(x=250, y=105)

    fill_a = tk.Button(windo, text="Fill Attendance", command=Fillattendances,
                       bg="SkyBlue1", width=20, height=2, activebackground="white", font=('times', 15, ' bold '))
    fill_a.place(x=250, y=160)


def admin_panel():
    win = tk.Toplevel(window)
    win.title("LogIn")
    win.geometry('880x420')
    win.configure(background='grey80')

    def log_in():
        username = un_entr.get()
        password = pw_entr.get()

        if username == 'vishal' and password == 'vishalreddy':
            win.destroy()  # Close the login window immediately on success

            try:
                student_details_path = os.path.join(
                    base_dir, 'StudentDetails', 'StudentDetails.csv')

                # 1. Check if the file exists at all
                if not os.path.exists(student_details_path):
                    messagebox.showinfo(
                        "Info", "No student details file found.\nPlease register a student using 'Take Images' first.", parent=window)
                    return

                # 2. Check if the file is empty
                if os.path.getsize(student_details_path) == 0:
                    messagebox.showinfo(
                        "Info", "The student details file is empty.\nPlease register a student.", parent=window)
                    return

                # 3. Only now, create the window and display the data
                root = tk.Toplevel(window)
                root.title("Student Details")
                root.configure(background='grey80')

                with open(student_details_path, newline="") as file:
                    reader = csv.reader(file)

                    # Display header row with a different style
                    header = next(reader)
                    for c_idx, col_name in enumerate(header):
                        label = tk.Label(root, width=15, height=1, fg="blue", font=(
                            'times', 13, ' bold '), bg="lightgrey", text=col_name, relief=tk.RIDGE)
                        label.grid(row=0, column=c_idx, padx=1, pady=1)

                    # Display data rows
                    for r_idx, col in enumerate(reader, 1):
                        for c_idx, row_val in enumerate(col):
                            label = tk.Label(root, width=15, height=1, fg="black", font=(
                                'times', 13), bg="white", text=row_val, relief=tk.RIDGE)
                            label.grid(row=r_idx, column=c_idx, padx=1, pady=1)

            except Exception as e:
                messagebox.showerror(
                    "Error", f"An error occurred: {e}", parent=window)

        else:
            valid = 'Incorrect ID or Password'
            Nt.configure(text=valid, bg="red", fg="white",
                         width=38, font=('times', 19, 'bold'))
            Nt.place(x=120, y=350)

    Nt = tk.Label(win, text="", bg="Green", fg="white",
                  width=40, height=2, font=('times', 19, 'bold'))

    un = tk.Label(win, text="Enter username : ", width=15, height=2,
                  fg="black", bg="grey", font=('times', 15, ' bold '))
    un.place(x=30, y=50)

    pw = tk.Label(win, text="Enter password : ", width=15, height=2,
                  fg="black", bg="grey", font=('times', 15, ' bold '))
    pw.place(x=30, y=150)

    def c00():
        un_entr.delete(first=0, last=22)

    un_entr = tk.Entry(win, width=20, bg="white",
                       fg="black", font=('times', 23))
    un_entr.place(x=290, y=55)

    def c11():
        pw_entr.delete(first=0, last=22)

    pw_entr = tk.Entry(win, width=20, show="*", bg="white",
                       fg="black", font=('times', 23))
    pw_entr.place(x=290, y=155)

    c0 = tk.Button(win, text="Clear", command=c00, fg="white", bg="black",
                   width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
    c0.place(x=690, y=55)

    c1 = tk.Button(win, text="Clear", command=c11, fg="white", bg="black",
                   width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
    c1.place(x=690, y=155)

    Login = tk.Button(win, text="LogIn", fg="black", bg="SkyBlue1", width=20, height=2,
                      activebackground="Red", command=log_in, font=('times', 15, ' bold '))
    Login.place(x=290, y=250)


def trainimg():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    global detector
    detector_path = os.path.join(
        base_dir, 'cascades', 'haarcascade_frontalface_default.xml')
    detector = cv2.CascadeClassifier(detector_path)

    training_image_dir = os.path.join(base_dir, 'TrainingImage')

    if not os.path.exists(training_image_dir) or not os.listdir(training_image_dir):
        l = 'Please put Images and then "Train Images"'
        Notification.configure(text=l, bg="red",
                               width=40, font=('times', 18, 'bold'))
        Notification.place(x=350, y=400)
        Notification.after(5000, Notification.place_forget)
        return

    try:
        faces, ids = getImagesAndLabels(training_image_dir)
        if len(ids) == 0:
            messagebox.showwarning(
                "Training Warning", "No faces were found in the training images. Please check your images.")
            return

        recognizer.train(faces, np.array(ids))

        training_image_label_dir = os.path.join(base_dir, 'TrainingImageLabel')
        os.makedirs(training_image_label_dir, exist_ok=True)
        model_path = os.path.join(training_image_label_dir, 'Trainner.yml')
        recognizer.save(model_path)

        res = "Model Trained Successfully"
        Notification.configure(text=res, bg="olive drab",
                               width=50, font=('times', 18, 'bold'))
        Notification.place(x=250, y=400)
        Notification.after(3000, Notification.place_forget)
    except Exception as e:
        messagebox.showerror(
            "Error", f"An error occurred during training: {e}")


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f)
                  for f in os.listdir(path) if f.endswith(('.jpg', '.png', '.jpeg'))]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            pilImage = Image.open(imagePath).convert('L')
            imageNp = np.array(pilImage, 'uint8')

            id_str = os.path.split(imagePath)[-1].split(".")[1]
            id_int = int(id_str)

            faces = detector.detectMultiScale(imageNp)

            for (x, y, w, h) in faces:
                faceSamples.append(imageNp[y:y + h, x:x + w])
                ids.append(id_int)
        except Exception as e:
            print(f"Could not process image {imagePath}: {e}")
            continue

    return faceSamples, ids


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()


window.protocol("WM_DELETE_WINDOW", on_closing)

message = tk.Label(window, text="Attendance Management System using Face Recognition",
                   bg="black", fg="white", width=50, height=3, font=('times', 30, ' bold '))
message.place(x=80, y=20)

Notification = tk.Label(window, text="All things good", bg="Green",
                        fg="white", width=15, height=3, font=('times', 17))

lbl = tk.Label(window, text="Enter Enrollment : ", width=20,
               height=2, fg="black", bg="grey", font=('times', 15, 'bold'))
lbl.place(x=200, y=200)


def testVal(inStr, acttyp):
    if acttyp == '1' and not inStr.isdigit():
        return False
    return True


txt = tk.Entry(window, validate="key", width=20,
               bg="white", fg="black", font=('times', 25))
txt['validatecommand'] = (txt.register(testVal), '%P', '%d')
txt.place(x=550, y=210)

lbl2 = tk.Label(window, text="Enter Name : ", width=20, fg="black",
                bg="grey", height=2, font=('times', 15, ' bold '))
lbl2.place(x=200, y=300)

txt2 = tk.Entry(window, width=20, bg="white", fg="black", font=('times', 25))
txt2.place(x=550, y=310)

clearButton = tk.Button(window, text="Clear", command=clear, fg="white", bg="black",
                        width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton.place(x=950, y=210)

clearButton1 = tk.Button(window, text="Clear", command=clear1, fg="white", bg="black",
                         width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton1.place(x=950, y=310)

AP = tk.Button(window, text="Check Registered students", command=admin_panel, fg="black",
               bg="SkyBlue1", width=19, height=1, activebackground="white", font=('times', 15, ' bold '))
AP.place(x=990, y=410)

takeImg = tk.Button(window, text="Take Images", command=take_img, fg="black", bg="SkyBlue1",
                    width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
takeImg.place(x=90, y=500)

trainImg = tk.Button(window, text="Train Images", fg="black", command=trainimg, bg="SkyBlue1",
                     width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
trainImg.place(x=390, y=500)

FA = tk.Button(window, text="Automatic Attendance", fg="black", command=subjectchoose,
               bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
FA.place(x=690, y=500)

quitWindow = tk.Button(window, text="Manually Fill Attendance", command=manually_fill, fg="black",
                       bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
quitWindow.place(x=990, y=500)

# This is the ONLY mainloop the application needs. It runs everything.
window.mainloop()
