from tkinter import *
from PIL import Image, ImageTk
import threading
import keyboard
import json
import time

# VERSION 1.2

root = Tk()
root.title("Self-Checkout")
root.geometry("800x480")

# DICTIONARIES
items = None
store_config = None
cart = []
total_price = 0
discounts = 0
accept_input = True

try:
    with open("items.json", "r") as f:
        items = json.load(f)
    with open("store_config.json", "r") as f:
        store_config = json.load(f)
    
except Exception as err:
    print("ERROR OPENING JSON FILES!")
    print(err)
    exit()
logoPath = store_config["logo"]
main_frame=None
main_panel_open = False
admin_frame=None
admin_panel_open = False
pay_frame=None
pay_panel_open = False


def create_popup(parent, title="", geometry="200x75", heading="", keypad=False, button=False, button_text="", button_command=None):
    global popup
    popup = Toplevel(parent)
    popup.title(title)
    popup.geometry(geometry)
    popup.attributes('-topmost', True)
    popup.transient(parent)
    popup.focus_force()
    try:
        alert.attributes("-toolwindow",True)
    except:
        pass

    popup.grid_columnconfigure(0, weight=1)
    popup.grid_columnconfigure(2, weight=1)

    label1 = Label(popup, text=heading, font=('none', 10, 'bold'))
    label1.grid(row=0, column=1, padx=5, pady=5)

    result = StringVar()

    if button:
        button1 = Button(popup, text=button_text, command=button_command)
        button1.grid(row=1, column=1)

    if keypad:
        input1 = Text(popup, width=23, height=1)
        input1.grid(row=1, column=1, padx=5)
        input1.focus()

        def entry(key):
            input1.insert(END, str(key))

        def enter():
            result.set(input1.get("1.0", "end-1c").strip())
            popup.destroy()

        keypad = Frame(popup)
        keypad.grid(row=2,column=1,pady=10)
        key1 = Button(keypad,text="1",command=lambda:entry(1),height=2,width=5,bg="gray",fg="white")
        key1.grid(row=0,column=0,padx=2,pady=2)
        key2 = Button(keypad,text="2",command=lambda:entry(2),height=2,width=5,bg="gray",fg="white")
        key2.grid(row=0,column=1,padx=2,pady=2)
        key3 = Button(keypad,text="3",command=lambda:entry(3),height=2,width=5,bg="gray",fg="white")
        key3.grid(row=0,column=2,padx=2,pady=2)
        key4 = Button(keypad,text="4",command=lambda:entry(4),height=2,width=5,bg="gray",fg="white")
        key4.grid(row=1,column=0,padx=2,pady=2)
        key5 = Button(keypad,text="5",command=lambda:entry(5),height=2,width=5,bg="gray",fg="white")
        key5.grid(row=1,column=1,padx=2,pady=2)
        key6 = Button(keypad,text="6",command=lambda:entry(6),height=2,width=5,bg="gray",fg="white")
        key6.grid(row=1,column=2,padx=2,pady=2)
        key7 = Button(keypad,text="7",command=lambda:entry(7),height=2,width=5,bg="gray",fg="white")
        key7.grid(row=2,column=0,padx=2,pady=2)
        key8 = Button(keypad,text="8",command=lambda:entry(8),height=2,width=5,bg="gray",fg="white")
        key8.grid(row=2,column=1,padx=2,pady=2)
        key9 = Button(keypad,text="9",command=lambda:entry(9),height=2,width=5,bg="gray",fg="white")
        key9.grid(row=2,column=2,padx=2,pady=2)
        key0 = Button(keypad,text="0",command=lambda:entry(0),height=2,width=5,bg="gray",fg="white")
        key0.grid(row=3,column=1,padx=2,pady=2)
        keyClear = Button(keypad,text="Clear",command=lambda:input1.delete("1.0","end"),height=2,width=5,bg="gray",fg="white")
        keyClear.grid(row=3,column=0,padx=2,pady=2)
        keyEnter = Button(keypad,text="Enter",command=enter,height=2,width=5,bg="gray",fg="white")
        keyEnter.grid(row=3,column=2,padx=2,pady=2)

    popup.wait_visibility()
    x = root.winfo_x() + root.winfo_width()//2 - popup.winfo_width()//2
    y = root.winfo_y() + root.winfo_height()//2 - popup.winfo_height()//2
    popup.geometry(f"+{x}+{y}")
    parent.wait_window(popup)
    popup.destroy()
    popup.update()
    return result.get()


def add_item(barcode):
    code_found = False
    global total_price,accept_input
    if accept_input:
        for item in items:
            if item["barcode"] == barcode:
                code_found = True
                print(item["barcode"],item["name"],item["price"])
                cart.append(item["barcode"])
                info_header.config(text=item["name"])
                if discounts >0:
                    new_price = round(item["price"]-item["price"]*discounts,2)
                    print(new_price)
                    price_display.config(text=f"${item['price']}")
                    item_list.insert(len(cart),f"{item['name']}  -  ${new_price}")
                    item_list.yview_moveto(1)
                    total_price += new_price
                    price_label.config(text=f"Total: ${total_price:.2f}")
                    discount_price.config(text=f"${new_price}")
                    item_count.config(text=f"{len(cart)} Items")
                else:
                    price_display.config(text=f"${item['price']}")
                    item_list.insert(len(cart),f"{item['name']}  -  ${item['price']}")
                    item_list.yview_moveto(1)
                    total_price += item["price"]
                    price_label.config(text=f"Total: ${total_price:.2f}")
                    item_count.config(text=f"{len(cart)} Items")
                total_price = round(total_price, 2)
                print(f"NEW TOTAL: {total_price}")
                
        if not code_found:
            print(f"Item '{barcode}' Not found!")
            alert = Tk()
            alert.title("Alert")
            alert.geometry("200x75")
            alert.attributes("-topmost",True)
            alert.eval('tk::PlaceWindow . center')
            try:
                alert.attributes("-toolwindow",True)
            except:
                None
            
            label1 = Label(alert,text=f"Item '{barcode}'\nNot Found!",font=('none',10,'bold'))
            button1 = Button(alert,text="Close",command=lambda:alert.destroy())
            label1.pack()
            button1.pack(pady=5)
            

def key_barcode():
    global accept_input
    accept_input = False
    value = create_popup(root,"","220x275","Enter Barcode:",True)
    if value:
        accept_input = True
        add_item(value)

def void_item():
    global item_list,total_price,cart
    selected = item_list.curselection()
    if selected:
        index = selected[0]
        print(f"Void item index {index}")
        for item in items:
            if item["barcode"] == cart[index]:
                if discounts>0:
                    item_list.delete(index)
                    new_price=round(item["price"]-item["price"]*discounts,2)
                    total_price -= new_price
                    cart.pop(index)
                    price_label.config(text=f"Total: ${total_price:.2f}")
                    item_count.config(text=f"{len(cart)} Items")  
                else:
                    item_list.delete(index)
                    total_price -= item["price"]
                    cart.pop(index)
                    price_label.config(text=f"Total: ${total_price:.2f}")
                    item_count.config(text=f"{len(cart)} Items")                
        print(total_price)
        print(cart)

def custom_discount():
    global accept_input
    accept_input = False
    value = create_popup(root,"","220x275","Enter Discount Amount (%):",True)
    if value:
        global discounts,discount_percent,total_price
        discounts += int(value)/100
        print(discounts)
        for i in cart:
            for item in items:
                if item["barcode"] == i:
                    total_price -= item["price"]
                    total_price += round(item["price"]-item["price"]*discounts,2)
                    print(total_price)
        if discounts > 0:
            discount_percent.config(text=f"Discounts: -{discounts*100}%")
        else:
            discount_percent.config(text="")
        price_label.config(text=f"Total: ${total_price:.2f}")
    accept_input = True

def close_lane():
    lane_off=Tk()
    lane_off.title("")
    lane_off.geometry("300x400")
    lane_off.attributes("-topmost",True)
    lane_off.eval('tk::PlaceWindow . center')
    try:
        alert.attributes("-toolwindow",True)
    except:
        None

    label1 = Label(lane_off,text="Lane Closed",font=('none',20,'bold'))
    label1.grid(row=0,column=0,padx=70,pady=50,sticky=NSEW)

def admin_panel():
    global item_display,main_frame,accept_input,close_lane
    if main_frame is not None:
        main_frame.grid_forget()
    accept_input = False
    main_panel_open = False
    pay_panel_open = False
    admin_panel_open = True
    
    admin_frame = Frame(root,bg="lightgray")
    admin_frame.grid(row=1, column=0, sticky="nsew")
    for widget in admin_frame.winfo_children():
        widget.destroy()
        
    def logout():
        global accept_input
        admin_frame.grid_forget()
        main_frame.grid(row=1, column=0, sticky="nsew")
        accept_input = True
    
    scrnTitle = Label(admin_frame,text="Staff Assistance Panel",bg="lightgray",font=('none',20,'bold'))
    scrnTitle.grid(row=0,column=0,padx=10,pady=10)
    button_panel = Frame(admin_frame,bg="lightgray",width=530,height=230)
    button_panel.grid(row=1,column=0,padx=10)
    button_panel.grid_propagate(False)

    void_btn = Button(button_panel,text="Void Item",command=void_item,bg="gray",fg="white",height=3,width=7)
    void_btn.grid(row=0,column=0,padx=5,pady=5)
    apply_discount = Button(button_panel,text="Apply\nDiscount",command=custom_discount,bg="gray",fg="white",height=3,width=7)
    apply_discount.grid(row=0,column=1,padx=5,pady=5)
    close_lane = Button(button_panel,text="⛔\nClose\nLane",command=close_lane,bg="gray",fg="white",height=3,width=7)
    close_lane.grid(row=0,column=2,pady=5,padx=5)
    exit_fullscrn = Button(button_panel,text="Exit\nFullscreen",command=lambda:root.attributes("-fullscreen",False),bg="gray",fg="white",height=3,width=7)
    exit_fullscrn.grid(row=0,column=3,pady=5,padx=5)
    enter_fullscrn = Button(button_panel,text="Enter\nFullscreen",command=lambda:root.attributes("-fullscreen",True),bg="gray",fg="white",height=3,width=7)
    enter_fullscrn.grid(row=0,column=4,pady=5,padx=5)

    button_panel.grid_columnconfigure(5, weight=1)
    button_panel.grid_rowconfigure(2, weight=1)
    logout = Button(button_panel,text="Logout/Exit >",command=logout,bg="red",fg="white",height=3,width=14)
    logout.grid(row=3,column=7,padx=10,pady=10,sticky=SE)
    
def assist_login():
    global accept_input
    accept_input = False
    value = create_popup(root,"","220x275","Scan or Enter staff code:",True)
    with open("login.json", "r") as f:
        data = json.load(f)
    print(data.get(value))
    if data.get(value) == "Staff":
        admin_panel()
    accept_input = True

def payment():
    global item_display,main_frame,accept_input,close_lane
    if main_frame is not None:
        main_frame.grid_forget()
    if admin_frame is not None:
        admin_frame.grid_forget()

    pay_frame = Frame(root,bg="lightgray")
    pay_frame.grid(row=1, column=0, sticky="nsew")
    for widget in pay_frame.winfo_children():
        widget.destroy()
        
    main_panel_open = False
    pay_panel_open = True
    admin_panel_open = False
    accept_input = False

    def back():
        global accept_input
        pay_frame.grid_forget()
        main_frame.grid(row=1, column=0, sticky="nsew")
        pay_panel_open = False
        main_panel_open = True
        accept_input = True

    def complete_payment():
        global popup,accept_input,cart,total_price,discounts
        popup.destroy()
        pay_frame.grid_forget()
        complete = Frame(root,width=550,bg="lightgray")
        complete.grid(row=1,column=0,sticky='nesw')
        complete.grid_propagate(False)
        complete.grid_rowconfigure(0, weight=1)
        complete.grid_rowconfigure(3, weight=1)
        complete.grid_columnconfigure(0, weight=1)
        complete.grid_columnconfigure(2, weight=1)
        title1 = Label(complete,text=f"Thank you for shopping at {store_config['store_name']}!",wraplength=450,bg="lightgray",font=('none',15,'bold'))
        title1.grid(row=1,column=1,pady=5,sticky='nesw')
        label1 = Label(complete,text="Please take your items and your receipt",bg="lightgray",font=('none',15))
        label1.grid(row=2,column=1,pady=10,sticky='nesw')
        root.update()
        time.sleep(5)
        complete.grid_forget()
        item_count.config(text="0 Items")
        info_header.config(text="Scan an item to start")
        price_display.config(text="-")
        discount_price.config(text="")
        discount_percent.config(text="")
        status_colourbar.config(bg="green")
        item_list.delete(0,END)
        price_label.config(text="Total: $0.00")
        cart = []
        total_price = 0
        discounts = 0
        back()
    
    def card():
        create_popup(root,geometry="200x85",title="",heading="Follow pinpad prompts\nto finalise payment",button=True,button_text="Complete",button_command=complete_payment)

    def cash():
        create_popup(root,geometry="200x85",title="",heading="Please insert notes\nand coins",button=True,button_text="Complete",button_command=complete_payment)
    
    accept_input = False
    scrnTitle = Label(pay_frame,text="Select Payment Method",bg="lightgray",font=('none',20,'bold'))
    scrnTitle.grid(row=0,column=0,padx=10,pady=10)
    button_panel = Frame(pay_frame,bg="lightgray",width=530,height=200)
    button_panel.grid(row=1,column=0,padx=10)
    button_panel.grid_propagate(False)

    if store_config["accept_cash"] == "True":
        cash_btn = Button(button_panel,text="💵\nCash",command=cash,font=('none',20))
        cash_btn.grid(row=0,column=0,padx=(170,20),pady=50)
    if store_config["accept_card"] == "True":
        card_btn = Button(button_panel,text="💳\nCard",command=card,font=('none',20))
        if store_config["accept_cash"] == "False":
            card_btn.grid(row=0,column=1,padx=(220,0),pady=50)
        else:
            card_btn.grid(row=0,column=1,pady=50)

    back_btn = Button(pay_frame,text="<  Back",command=back,font=('none',12,'bold'))
    back_btn.grid(row=2,column=0,padx=10,pady=5,sticky=W)
    
def main():
    global logo, logo_image, top_label, item_count,main_frame,admin_frame
    global item_display, info_header, price_display, discount_price, discount_percent
    global status_colourbar, item_list, price_label, pay_button, bottom_row, assistance_btn, key_code

    main_frame = Frame(root)
    main_frame.grid(row=1, column=0, sticky="nsew")
    main_panel_open = True
    
    image = Image.open(logoPath)
    logo = ImageTk.PhotoImage(image)
    logo_image = Label(root, image=logo)
    logo_image.grid(row=0,column=0,padx=10,pady=10,sticky=W)

    top_label = Label(root,text=f"Welcome to {store_config['store_name']}!",font=('none',15,'bold'))
    top_label.grid(row=0,column=0,sticky=W,padx=(180,0))
    item_count = Label(root,text="0 Items",font=('none','10','bold'))
    item_count.grid(row=0,column=2,sticky=S)


    item_display = Frame(main_frame,width=550,height=306,bg="lightgray")
    item_display.grid(row=1,column=0,sticky=N)
    item_display.grid_propagate(False)
    item_display.grid_columnconfigure(1, weight=1)
    item_display.grid_rowconfigure(1, weight=1)

    info_header = Label(item_display,text="Scan an item to start",wraplength=450,font=('none',20),bg="lightgray")
    info_header.grid(row=0,column=0,padx=10,pady=10)

    price_display = Label(item_display,text="-",bg="lightgray",font=('none',15))
    price_display.grid(row=0,column=2,padx=(0,10),sticky=E)

    discount_price = Label(item_display,text="",bg="lightgray",fg="red",font=('none',20,'bold'))
    discount_price.grid(row=1,column=2,sticky=N)

    discount_percent = Label(item_display,text="",bg="lightgray",fg="red",font=('none',10,'bold'))
    discount_percent.grid(row=2,column=0,padx=10,sticky=W)

    status_colourbar = Frame(item_display, width=530,height=10,bg="green")
    status_colourbar.grid(row=3,column=0,columnspan=3,pady=10,sticky=S)

    item_list = Listbox(root,width=30,height=17)
    item_list.grid(row=1,column=2,padx=3)
    price_label = Label(root,text="Total: $0.00",font=('none',15,'normal'))
    price_label.grid(row=3, column=2)
    pay_button = Button(root,text="Pay Now",command=payment,bg=store_config['theme_colour'],fg="white",width=15,height=2,font=("none",15,"bold"))
    pay_button.grid(row=4,column=2)

    bottom_row = Frame(root,width=550,height=100)
    bottom_row.grid(row=3,column=0,columnspan=2,rowspan=2)
    bottom_row.grid_propagate(False)

    assistance_btn = Button(bottom_row,text="Assistance\nLogin",command=assist_login,height=4,width=8,font=('none',10,'bold'))
    assistance_btn.grid(row=0,column=0,padx=10,pady=12)

    key_code = Button(bottom_row,text="Key in code",command=key_barcode,height=4,width=24,font=('none',10,'bold'))
    key_code.grid(row=0,column=1)
            
def input_handler():
    global hidden_entry
    hidden_entry = Entry(root)
    hidden_entry.place(x=-100, y=-100)

    def keep_focus():
        if accept_input:
            hidden_entry.focus_force()
        root.after(100, keep_focus)
        
    def on_enter(event):
        global accept_input
        code = hidden_entry.get().strip()
        hidden_entry.delete(0, END)
        if code and accept_input:
            print(f"Scanned: {code}")
            status_colourbar.config(bg="red")
            add_item(code)
            root.after(700, lambda: status_colourbar.config(bg="green"))

    hidden_entry.bind("<Return>", on_enter)
    keep_focus()
        
            
thread1 = threading.Thread(target=input_handler, daemon=True)
thread1.start()
main()
root.mainloop()


    
