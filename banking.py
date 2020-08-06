from random import seed, randint
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS card (
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0);''')

seed()
exit = 1


def make_num(n):
    number = ''
    for i in range(n):
        number += str(randint(0, 9))
    return number

def luhn_alg(card):
    reserve = ''
    total = 0
    for n in range(len(card)):
        if (n + 1) % 2 == 1:
            if int(card[n]) > 4:
                reserve += str((int(card[n]) * 2) - 9)
            else:
                reserve += str(int(card[n]) * 2)
        else:
            reserve += card[n]
        total += int(reserve[n])
    return total

def check_luhn_alg(new_card):
    return luhn_alg(new_card) % 10 == 0

def apply_luhn_alg():
    new_card = '400000' + make_num(9)
    last_digit = 10 - (luhn_alg(new_card) % 10)
    if last_digit == 10:
        last_digit = 0
    return new_card + str(last_digit)

def add_income(info,income):
    cur.execute('''UPDATE card
                           SET balance=:income
                           WHERE number=:num''',{'income': info[3]+income,'num': info[1]})
    conn.commit()
def reduce_income(info,income):
    cur.execute('''UPDATE card
                    SET balance=:income
                    WHERE number=:num''',{'income': info[3]-income,'num': info[1]})
    conn.commit()

def transfer(info_first_card,info_second_card,income):
    reduce_income(info_first_card,income)
    add_income(info_second_card,income)

# card_info[n]:
# 0 - id
# 1 - number
# 2 - pin
# 3 - balance

def create_card():
    cur.execute('SELECT * FROM card')
    id_calc = len(cur.fetchall()) + 1
    new_card = apply_luhn_alg()
    new_pin = make_num(4)
    cur.execute("""INSERT INTO card VALUES(?,?,?,?)""",
                (id_calc, new_card, new_pin, 0))
    conn.commit()


def transaction(info):
    print("Enter card number:")
    new_card = input()
    if new_card == info[1]:
        print("You can't transfer money to the same account!")
        print()
    elif not check_luhn_alg(new_card):
        print("Probably you made mistake in the card number. Please try again!")
        print()
    else:
        cur.execute('''SELECT * FROM card
                       WHERE number=:num''',{'num': new_card})
        second_info = cur.fetchone()
        if second_info is None:
            print("Such a card does not exist.")
            print()
        else:
            print("Enter how much money you want to transfer:")
            sum = int(input())
            if sum > info[3]:
                print("Not enough money!")
                print()
            else:
                transfer(info,second_info,sum)
                print("Success!")
                print()


def log_in(info):
    is_log_in = 1
    while is_log_in:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
        print()

        answer = int(input())

        if answer == 0:
            is_log_in = 0
            global exit
            exit = 0
        elif answer == 1:
            print("Balance:", info[3])
        elif answer == 2:
            print("Enter income:")
            income = int(input())
            add_income(info,income)
            cur.execute('''SELECT * FROM card
                           WHERE id=:num''',{'num': info[0]})
            info = cur.fetchone()
            print("Income was added!")
            print()

        elif answer == 3:
            transaction(info)

        elif answer == 4:
            cur.execute('''DELETE FROM card
                           WHERE id=:num''',{'num': info[0]})
            is_log_in = 0
            conn.commit()

        elif answer == 5:
            print("You have successfully logged out!")
            is_log_in = 0


while exit:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")

    answer = int(input())

    if answer == 0:
        exit = 0
    if answer == 1:
        create_card()
        cur.execute('SELECT * FROM card')
        cur.execute('''SELECT * 
                    FROM card 
                    WHERE id=:num''', {'num': len(cur.fetchall())})
        card_info = cur.fetchone()
        print("Your card has been created")
        print("Your card number:")
        print(card_info[1])
        print("Your card PIN:")
        print(card_info[2])
        print()

    elif answer == 2:
        print("Enter your card number:")
        login = input()
        print("Enter your PIN:")
        password = input()
        cur.execute('''SELECT *
                       FROM card
                       WHERE number=:num''', {'num': login})
        card_info = cur.fetchone()
        if card_info is not None and password == card_info[2]:
            print("You have successfully logged in!")
            print()
            log_in(card_info)
        else:
            print("Wrong card number or PIN!")
            print()

conn.close()
print("Bye!")
