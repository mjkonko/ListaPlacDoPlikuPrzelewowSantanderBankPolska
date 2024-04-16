import camelot
import re
import pandas as pd

#Global variables
global global_sender_account_number
global_sender_account_number = "1234567890"

# Local storage for extracted data
payment_objects = []
employee_info = []     
error_list = []
cash_payments = []

# Provide the path to your PDF file
pdf_path = 'e.pdf'

class EmployeeTransferDetails():
    receipient_account_number = ""
    sender_account_number = global_sender_account_number
    name = ""
    address = ""
    amount = ""
    type = ""
    title = "Wypłata"
    type_2 = "" #0 - internal transfer, 1 - external elixir transfer
    is_cash = False
    
    def __init__(self, receipient_account_number, name, address, amount, type, title, type_2):
        self.receipient_account_number = receipient_account_number
        self.name = name
        self.address = address
        self.amount = amount
        self.type = type
        self.title = title
        self.type_2 = type_2
        
class Payment():
    name = ""
    amount = ""
    is_cash = False


def extract_name_salary_from_pdf():
    # extract all the tables in the PDF file
    tables = camelot.read_pdf(pdf_path, pages='all')
    # generate objects with values from the second and the last columns for all of the rows
    
    for table in tables:
        for row in table.df.iloc[1:-3].itertuples(index=False):
            payment_pdf = Payment()
            
            payment_pdf.name = ''.join(filter(lambda x: not x.isdigit() and x not in ['[', ']', '/', ','], row[1]))
            payment_pdf.name = payment_pdf.name.replace("  PLN  mies.", " ")
            
            # extract only the number that follows after "ROR:"
            payment_pdf.amount = row[-1]
            pattern = r'ROR:\s*([\d\s,]*)'
            match = re.search(pattern, row[-1])
            if match:
                payment_pdf.amount = match.group(1).replace(" ", "")
                
            # make object.name in one line
            payment_pdf.name = payment_pdf.name.replace("\n", "")
            # clean up whitespaces in all object fields
            payment_pdf.name = payment_pdf.name.strip().replace("|", " ") 
            payment_pdf.amount = payment_pdf.amount.strip().replace("|", " ") 
            
            if payment_pdf.amount == "0,00":
                payment_pdf.is_cash = True
                
            if payment_pdf.name != "" and payment_pdf.is_cash == False:
                payment_objects.append(payment_pdf)
    
    # print payment error objects list
    for payment in payment_objects:
        if payment.name == "" or payment.amount == "0,00" or payment.amount == "":
            print(f"ERROR! Name: {payment.name}, Amount: {payment.amount}") 
            error_list.append(payment)

def get_txt_employee_info():
    # Read the text file
    with open('przelewy_baza.txt', 'r', encoding='windows-1250') as file:
        lines = file.readlines()
    # Create an empty data frame
    df = pd.DataFrame(columns=['Type', 'Account Number', 'Recipient Account Number', 'Name', 'Address', 'Amount', 'Interal/Elixir', 'Title'])
    
    # Iterate over each line in the text file
    for line in lines[1:]:
        # Split the line by '|'
        data = line.strip().split('|')
        # Create a dictionary with the data
        row = {
            'Type': data[0].replace("|", " "),
            'Account Number': data[1].replace("|", " "),
            'Recipient Account Number': data[2].replace("|", " "),
            'Name': data[3].replace("|", " "),
            'Address': data[4].replace("|", " "),
            'Amount': "",
            'Interal/Elixir': data[6].replace("|", " "),
            'Title': data[7].replace("|", " ") 
        }
        # Append the row to the data frame
        df = df._append(row, ignore_index=True) # type: ignore
        
        # Create an EmployeeTransferDetails object
        employee = EmployeeTransferDetails(data[2], data[3], data[4], "", data[0], data[7], data[6])
        employee_info.append(employee);

def add_amounts_to_employee_info():
    # Iterate over the payment objects    
    for payment in payment_objects:
        # Iterate over the employee objects
        for employee in employee_info:
            # Check if the names match
            if payment.name in employee.name:
                # Add the amount to the employee object
                employee.amount = payment.amount

    # Return the employee_info list
    return employee_info

extract_name_salary_from_pdf()
get_txt_employee_info()
employee_info = add_amounts_to_employee_info()

# Print the employee_info list
#for employee in employee_info:
    #print(f"Name: {employee.name}, Amount: {employee.amount}, Account Number: {employee.receipient_account_number}, Type: {employee.type}, Title: {employee.title}, Type_2: {employee.type_2}")

if (len(error_list) > 0):
    print("ERROR! There are some errors in the data extraction. Please check the output above!")
    print("The following employees have errors:")  
    for error in error_list:
        print(f"Name: {error.name}, Amount: {error.amount}")
else:
    with open('output.txt', 'w', encoding='windows-1250') as file:
        file.write("4120414|1")
        # Write to file in format type|rercipient_account_number|sender_account_number|name|address|amount|type_2|title
        for employee in employee_info:
            file.write(f"\n{employee.type}|{employee.sender_account_number}|{employee.receipient_account_number}|{employee.name}|{employee.address}|{employee.amount}|{employee.type_2}|{employee.title}|")
                
    print("Successfull creation of output file!")