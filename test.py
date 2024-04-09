import camelot
import re
import pandas as pd

#Global variables
global global_sender_account_number
global_sender_account_number = "11 1234 5678 9012 3456 1234 5678 9012"

# Local storage for extracted data
payment_objects = []
employee_info = []     

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
            payment_pdf.name = payment_pdf.name.strip() 
            payment_pdf.amount = payment_pdf.amount.strip()
            
            if payment_pdf.name != "":
                payment_objects.append(payment_pdf)
    
    # print payment objects list
    for payment in payment_objects:
        print(f"Name: {payment.name}, Amount: {payment.amount}")    
    print("Successfull extraction of data from PDF file!")
    
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
            'Type': data[0],
            'Account Number': data[1],
            'Recipient Account Number': data[2],
            'Name': data[3],
            'Address': data[4],
            'Amount': "",
            'Interal/Elixir': data[6],
            'Title': data[7]
        }
        # Append the row to the data frame
        df = df._append(row, ignore_index=True)
        
        # Create an EmployeeTransferDetails object
        employee = EmployeeTransferDetails(data[2], data[3], data[4], "", data[0], data[7], data[6])
        employee_info.append(employee);

    # Return the data frame
    #print(df.head())
    print("Successfull extraction of data from TXT 'database' file!")
        
    #print(employee_info)
    print("Successfull creation of EmployeeTransferDetails objects!")

def add_amounts_to_employee_info():
    # Iterate over the payment objects
    print("Adding amounts to EmployeeTransferDetails objects")
    
    for payment in payment_objects:
        print(f"P Name: {payment.name}, Amount: {payment.amount}")
        # Iterate over the employee objects
        for employee in employee_info:
            print(f"E Name: {employee.name}, Amount: {employee.amount}")
            # Check if the names match
            if employee.name in payment.name:
                # Add the amount to the employee object
                employee.amount = payment.amount
                print(f"Added amount: {employee.amount} to employee: {employee.name} from payment: {payment.name}")

    # Return the employee_info list
    return employee_info



extract_name_salary_from_pdf()
get_txt_employee_info()
employee_info = add_amounts_to_employee_info()

# Print the employee_info list
for employee in employee_info:
    #print(f"Name: {employee.name}, Amount: {employee.amount}")
    print(f"Name: {employee.name}, Amount: {employee.amount}, Account Number: {employee.receipient_account_number}, Type: {employee.type}, Title: {employee.title}, Type_2: {employee.type_2}")

print()

#with open('output.txt', 'w') as file:
    #for name, amount in employee_info:
        #file.write(f"Name: {name}, Amount: {amount}\n")
        
