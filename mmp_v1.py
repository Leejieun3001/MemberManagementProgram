from tkinter import *
from datetime import *
import random
import time
import threading
from tkinter import messagebox
import pymysql

class MainClass(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("MMP")
        self.geometry("250x250")
        
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (LoginPage,ReservationPage,ManagerLoginPage,ManagerPage,MyPage):       
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("LoginPage")
        
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


#-------------------- 수업조회 페이지 --------------------
class ReservationPage(Frame):
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        t = ['월', '화', '수', '목', '금', '토', '일']
        self.controller = controller
        label = Label(self, text="This is Reservationpage")
        label.pack(side="top", fill="x", pady=10)
        
        '''conn = pymysql.connect(host = 'localhost', user = 'root', password = '1234' ,db = 'MMP')
        # Connection 으로부터 Cursor 생성
        curs = conn.cursor()
 
        # SQL문 실행
        sql = "select * from class"
        curs.execute(sql)
 
        # 데이타 Fetch
        rows = curs.fetchall()
        print(rows)     # 전체 rows
        # print(rows[0])  # 첫번째 row: (1, '김정수', 1, '서울')
        # print(rows[1])  # 두번째 row: (2, '강수정', 2, '서울')
        # Connection 닫기
        conn.close()

        for i in range(0,5):
            dt = datetime.now()
            nowYear = dt.year
            nowMonth = dt.month
            nowDay = dt.day
            nextDt = dt + timedelta(days = i)
            newYear = nextDt.year
            newMonth = nextDt.month
            newDay = nextDt.day
            newDate = t[nextDt.weekday()]
            date = str(newYear) +" / "+ str(newMonth) + " / " + str(newDay) + " (" + newDate +")"
            name = rows[i]
            btn1 = Button(self, text = name)
            btn1.pack()'''

        logoutBtn = Button(self, text = "Logout",
                          command=lambda: controller.show_frame("LoginPage"))
        
        logoutBtn.pack()
#---------------------------------------------------------

#-------------------- 관리자 페이지 --------------------
class ManagerLoginPage(Frame):
    ##관리자 로그인 페이지 프레임
    def __init__(self, parent, controller):
        ###mngpw : 관리자 비밀번호
        self.mngpw="password"
        
        Frame.__init__(self, parent)
        self.controller = controller

        Label(self, text="관리자 비밀번호", padx=15, pady=10).grid(row=0, column=0, sticky="W")

        ###mngpwSV : 입력한 관리자 비밀번호
        self.mngpwSV = StringVar("")
        ###mngpwE : 관리자 비밀번호 입력 Entry
        self.mngpwE = Entry(self, show="*", textvariable=self.mngpwSV)
        self.mngpwE.grid(padx=15, row=1, column=0)
        ###trymnglog : 관리자 로그인 초기화
        self.trymnglog=-1
        self.mngpwE.bind("<Return>", self.bemng)

        ###mnglogB : 관리자 로그인 버튼
        mnglogB = Button(self, text="입력", width=5, command=self.mnglog)
        mnglogB.grid(row=1, column=1)

    ##bemng : 관리자 로그인 시도(enter) 함수
    def bemng(self, event):
        ###관리자 로그인 시도 중
        self.trymnglog=0
        if(self.trymnglog==0):
            self.mnglog()
            ###trymnglog : 관리자 로그인 초기화
            self.trymnglog=-1

    ##mnglog : 관리자 로그인 함수
    def mnglog(self):
        ###관리자 비밀번호와 입력한 관리자 비밀번호가 같으면 로그인 성공
        if(self.mngpw==str(self.mngpwSV.get())):
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)
            ####관리자 페이지 열기
            self.controller.show_frame("ManagerPage")
        ###로그인 실패
        else:
            ####실패 메세지박스 보이기
            messagebox.showinfo("information", "비밀번호가 틀렸습니다.")
            ####Entry에 입력한 내용 초기화
            self.mngpwE.delete(0,END)

class ManagerPage(Frame):
    ##관리자 페이지 프레임
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        ####tryadd : 수업/회원 등록 프레임 초기화
        self.tryadd=-1
        self.tryaddClass()

        ###addcpB/addmpB : 회원/수업 등록 프레임 변경 라디오 버튼
        self.addcpRB = Radiobutton(self, text="수업등록", value=0, command=self.tryaddClass)
        self.addcpRB.grid(row=0, column=0, sticky="W")
        self.addmpRB = Radiobutton(self, text="회원등록", value=1, command=self.tryaddMember)
        self.addmpRB.grid(row=0, column=0)
        ###mnglogoutB : 관리자 로그아웃 버튼
        mnglogoutB = Button(self, text="관리자 로그아웃", command=lambda: self.controller.show_frame("ManagerLoginPage"))
        mnglogoutB.grid(row=2, column=0, sticky="E", pady=70)
    
    ##tryaddClass : 수업 등록 프레임
    def tryaddClass(self):
        ###수업 등록 중
        self.tryadd=0
        ###addcF : 수업 등록 프레임
        self.addcF = Frame(self)
        self.addcF.grid(row=1, column=0)

        ###cName : 수업이름
        Label(self.addcF, text="이　름", padx=20).grid(row=1, column=0)
        self.cName = Entry(self.addcF)
        self.cName.grid(row=1, column=1)

        ###cDate : 수업날짜
        Label(self.addcF, text="날　짜", padx=20).grid(row=2, column=0)
        self.cDate1 = Entry(self.addcF, width=5)
        self.cDate1.grid(row=2, column=1, sticky="W")
        self.cDate2 = Entry(self.addcF, width=5)
        self.cDate2.grid(row=2, column=1)
        self.cDate3 = Entry(self.addcF, width=5)
        self.cDate3.grid(row=2, column=1, sticky="E")

        ###mLimit : 수업인원
        Label(self.addcF, text="인　원", padx=20).grid(row=3, column=0)
        self.mLimit = Entry(self.addcF)
        self.mLimit.grid(row=3, column=1)

        ###addcB : 수업등록 버튼
        addcB = Button(self.addcF, text="등록", command=self.addClick, width=5)
        addcB.grid(row=7, column=1, sticky="E", pady=5)
        
    ##tryaddMember : 회원 등록 프레임
    def tryaddMember(self):
        ###회원 등록 중
        self.tryadd=1
        ###addmF : 회원 등록 프레임
        self.addmF = Frame(self)
        self.addmF.grid(row=1, column=0)

        ###mbNae : 회원이름
        Label(self.addmF, text="이　름", padx=20).grid(row=1, column=0)
        self.mbName = Entry(self.addmF)
        self.mbName.grid(row=1, column=1)

        ###mbNum : 회원번호
        Label(self.addmF, text="번　호", padx=20).grid(row=2, column=0)
        self.mbNum1 = Entry(self.addmF, width=5)
        self.mbNum1.grid(row=2, column=1, sticky="W")
        self.mbNum2 = Entry(self.addmF, width=5)
        self.mbNum2.grid(row=2, column=1)
        self.mbNum3 = Entry(self.addmF, width=5)
        self.mbNum3.grid(row=2, column=1, sticky="E")

        ###rTime : 잔여횟수
        Label(self.addmF, text="횟　수", padx=20).grid(row=3, column=0)
        self.rTime = Entry(self.addmF)
        self.rTime.grid(row=3, column=1)

        ###addmB : 회원등록 버튼
        addmB = Button(self.addmF, text="등록", command=self.addClick, width=5)
        addmB.grid(row=4, column=1, sticky="E", pady=5)

    ##addClick : 등록 버튼 클릭 함수
    def addClick(self):
        ###등록 질문 메세지박스
        if (messagebox.askokcancel("Redirecting", "등록하시겠습니까?")):
            ###확인 버튼 클릭 시
            ####데이터베이스 연결
            self.conn=pymysql.connect(host="127.0.0.1", user="root", passwd="1234", db="mmp")
            self.cur = self.conn.cursor()
            ####입력 내용 오류 확인 및 등록
            if (self.tryadd==0):
                if(len(self.cDate1.get())!=4 or (int(self.cDate2.get())<1 or int(self.cDate2.get())>12) or (int(self.cDate3.get())<1 or int(self.cDate3.get())>31)) :
                    messagebox.showinfo("information","등록 실패")
                else:self.addClass()
            elif (self.tryadd==1):
                if(str(self.mbNum1.get())!="010" or (len(self.mbNum2.get()) and len(self.mbNum3.get()))!=4):
                    messagebox.showinfo("information","등록 실패")
                else:self.addMember()
            ###데이터베이스 닫기
            self.conn.close()
                
    ##addClass : 수업등록 함수
    def addClass(self):
        try :
            sql = "INSERT INTO class(cname, cdate, mlimit) VALUES (%s, %s, %s)"
            val=(str(self.cName.get()), str(self.cDate1.get())+"/"+str(self.cDate2.get())+"/"+str(self.cDate3.get()), int(self.mLimit.get()))
            print(val)
            self.cur.execute(sql,val)
            print("수업등록:", val)
            self.conn.commit()
            ###Entry에 입력한 내용 초기화
            self.cName.delete(0,END)
            self.cDate1.delete(0,END)
            self.cDate2.delete(0,END)
            self.cDate3.delete(0,END)
            self.mLimit.delete(0,END)
        except :
            self.conn.rollback()
            messagebox.showinfo("information","등록 실패")  

    ##addMember : 회원등록 함수
    def addMember(self):
        ###SQL문 실행
        try :
            sql = "INSERT INTO member(mname, mnum, rtime) VALUES (%s, %s, %s)"
            val=(str(self.mbName.get()), str(self.mbNum1.get())+str(self.mbNum2.get())+str(self.mbNum3.get()), int(self.rTime.get()))
            self.cur.execute(sql,val)
            self.conn.commit()
            ###Entry에 입력한 내용 초기화
            self.mbName.delete(0,END)
            self.mbNum1.delete(0,END)
            self.mbNum2.delete(0,END)
            self.mbNum3.delete(0,END)
            self.rTime.delete(0,END)
        ###데이터 입력 실패
        except :
            self.conn.rollback()
            messagebox.showinfo("information","등록 실패")  

    ##mnglogout : 관리자 페이지 로그아웃 함수
    def mnglogout(self):
        ###프레임 초기화
        self.resetmn()
        self.tryadd=-1
        ###페이지 이동
        self.controller.show_frame("ReservationPage")
#-------------------------------------------------------

#-------------------- 마이 페이지 --------------------
class MyPage(Frame):
    
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="This is MyPage 1")
        label.pack(side="top", fill="x", pady=10)

        logoutBtn = Button(self, text = "Logout",
                          command=lambda: controller.show_frame("LoginPage"))
        logoutBtn.pack()
#-----------------------------------------------------

#-------------------- 로그인 페이지 --------------------
class LoginPage(Frame):
    ##로그인 프레임
    def __init__(self, parent, controller):
        self.lognum="12345"
        
        Frame.__init__(self, parent)
        self.controller = controller

        Label(self, text="회원번호", padx=15, pady=10).grid(row=0, column=0, sticky="W")

        ###logID : 회원번호 Entry
        self.logID = Entry(self)
        self.logID.grid(padx=15, row=1, column=0)
        ###trylog : 로그인 초기화 인수
        self.trylog=-1
        self.logID.bind("<Return>", self.belog)

        ###btnLogin : 로그인 버튼
        btnLogin = Button(self, text="로그인", command=self.log)
        btnLogin.grid(row=1, column=1)

    ##belog : 로그인 시도(enter) 함수
    def belog(self, event):
        ###로그인 시도 중
        self.trylog=0
        if(self.trylog==0):
            self.log()
            ###trylog : 로그인 초기화
            self.trylog=-1

    ##log : 로그인 함수
    def log(self):
        ###회원번호와 입력한 회원번호가 같으면 로그인 성공
        if(self.lognum==str(self.logID.get())):
            ####Entry에 입력한 내용 초기화
            self.logID.delete(0,END)
            ####관리자 페이지 열기
            self.controller.show_frame("ReservationPage")
            ###mb : 프레임 전환 메뉴
            mb=Menu(self.controller)
            mb.add_command(label="수업조회", command=lambda: self.controller.show_frame("ReservationPage"))
            mb.add_command(label="마이페이지", command=lambda: self.controller.show_frame("MyPage"))
            mb.add_command(label="관리자페이지", command=lambda: self.controller.show_frame("ManagerLoginPage"))
            self.controller.config(menu=mb)
        ###로그인 실패
        else:
            ####실패 메세지박스 보이기
            messagebox.showinfo("information", "등록된 회원번호가 아닙니다.")
            ####Entry에 입력한 내용 초기화
            self.logID.delete(0,END)
#-------------------------------------------------------        

        
if __name__ == "__main__":
    app = MainClass()
    app.mainloop()
