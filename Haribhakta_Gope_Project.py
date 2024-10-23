# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 00:21:04 2022

@author: harig
"""

import statistics as stats
import numpy as np

POSITIVE_WORDS = {"excellent", "good", "dependable"}
NEGATIVE_WORDS = {"poor", "error", "unreliable", "late"}


class EmployeePerformances:
    """
    A class that implements analysis of annual employee performance for ABC Consulting professional staff
    """

    def __init__(self, init_data_path="emp_beg_yr.txt", sales_path="sales.txt"):
        # initialize a main dictionary that will contain employee performance
        self.employee_performances = dict()
        self.performanceMatrix = dict()

        # initial data for all employees
        with open(init_data_path) as file:
            file_lines = file.readlines()

        # generate initial dictionary,
        # use an employee ID as a key and dictionary that contains employee information as a value
        for line in file_lines[1:]:
            Id, last_name, first_name, job_code, base_pay = line.strip().split(",")
            self.employee_performances[Id] = dict(
                last_name=last_name, first_name=first_name, job_code=job_code, base_pay=int(
                    base_pay)
            )

        # load new sales (only for Directors)
        sales = dict()
        with open(sales_path) as file:
            file_lines = file.readlines()

        for line in file_lines:
            Id, sale = line.split(",")
            sales[Id] = int(sale)

        # add sales to the main dictionary
        for Id, item in self.employee_performances.items():
            if item["job_code"] == "D":
                if Id not in sales:
                    # if new sale is not provided for a Director, set a sale to zero
                    self.employee_performances[Id]["sale"] = 0
                else:
                    self.employee_performances[Id]["sale"] = sales[Id]

        self.employees_Ids = set(self.employee_performances.keys())
        emp_sale_ids = set(sales.keys())
        error_Ids = emp_sale_ids.difference(self.employees_Ids)
        with open("error.txt", "a") as file:
            for Id in error_Ids:
                file.write(f"{Id} in Sale.txt\n")

    def hours_worked(self, path="timesheet.txt"):
        # a method that calculates utilization rate
        hours_worked_per_employee = dict()

        # load the data from the file
        with open(path, "r") as file:
            file_lines = file.readlines()

        # iterate over all records and calculate total hours worked annually for each emplolyee
        for line in file_lines:
            Id, hours_worked_per_project = line.split(",")
            if Id not in hours_worked_per_employee:
                hours_worked_per_employee[Id] = 0
            hours_worked_per_employee[Id] += int(hours_worked_per_project)

        # calculate utilization rate and add it to the main dictionary
        # if employee not have had any engagement in the year, set utilization rate to zero
        for Id in self.employee_performances.keys():
            if Id in hours_worked_per_employee:
                hours = hours_worked_per_employee[Id]
                score = int(round(100 * hours / 2250))
                self.employee_performances[Id]["utilization"] = score
            else:
                self.employee_performances[Id]["utilization"] = 0

        hours_worked_per_employee_Ids = set(hours_worked_per_employee.keys())

        error_Ids = hours_worked_per_employee_Ids.difference(
            self.employees_Ids)
        with open("error.txt", "a") as file:
            for Id in error_Ids:
                file.write(f"{Id} in timesheet.txt\n")

    def textual_evaluation(self, path="evaluation.txt"):
        # a method that evaluation score from comments
        employee_textual_evaluation = dict()

        # load comments from the file
        with open(path, "r") as file:
            file_lines = file.readlines()

        for line in file_lines:
            Id, text_eval = line.split("#")
            # count the number of negative and possutive words in each comment
            neg_words_count = sum([text_eval.lower().count(word)
                                  for word in NEGATIVE_WORDS])
            pos_words_count = sum([text_eval.lower().count(word)
                                  for word in POSITIVE_WORDS])
#             print(Id ,"positive ={} neg = {}".format(pos_words_count,neg_words_count))
            if pos_words_count + neg_words_count > 0:
                # calculate the score
                score = 100 * (pos_words_count - neg_words_count) / \
                    (pos_words_count + neg_words_count)
                score = int(round(score))
                employee_textual_evaluation[Id] = score
            else:
                score = 0
                employee_textual_evaluation[Id] = score

        self.employees_Ids = set(self.employee_performances.keys())
        for Id, item in self.employee_performances.items():
            if item["job_code"] == "C":
                if Id in employee_textual_evaluation:
                    score = employee_textual_evaluation[Id]
                    self.employee_performances[Id]["Evaluation score"] = score
                else:
                    self.employee_performances[Id]["Evaluation score"] = 0

        evaluation_Emp_ids = set(employee_textual_evaluation.keys())
        error_Ids = evaluation_Emp_ids.difference(self.employees_Ids)
        with open("error.txt", "a") as file:
            for Id in error_Ids:
                file.write(f"{Id} in evaluation.txt\n")

    def calculate_bonus(self, rate=0):
        # a method that calculate employee bonus base on the rate
        employee_bounds = dict()
        total_bonus_payout = 0
        for Id, item in self.employee_performances.items():
            if item["job_code"] == "C":
                # for Consultants
                if (item['utilization'] > 75) & (item["Evaluation score"] >= 50):
                    base_pay = item['base_pay']
                    bonus = int(round(base_pay * (rate / 100)))
                    bonus = bonus if bonus < 50000 else 50000
                    total_bonus_payout = total_bonus_payout + bonus
                    self.employee_performances[Id]['Bonus'] = bonus
                else:
                    self.employee_performances[Id]['Bonus'] = 0

            else:
                # For Directores
                if item['utilization'] > 75:

                    total_sale = item['sale']
                    bonus = int(round(total_sale * (rate / 100)))
                    bonus = bonus if bonus < 150000 else 150000
                    total_bonus_payout = total_bonus_payout + bonus
                    self.employee_performances[Id]['Bonus'] = bonus
                else:
                    self.employee_performances[Id]['Bonus'] = 0

        print("Bonus rate = {}% \nTotal Bonus Payout = {} ".format(
            rate, total_bonus_payout))

    def Finalized_rate(self):
        ans = ""
        while ans.lower() != "no":
            rate = 0
            try:
                rate = float(input("Please Enter the Bonus Rate  :"))
                self.calculate_bonus(rate)
                print("\n")
                ans = input("Do you want to try other Rate ? (Yes/No)")
            except ValueError:
                print("Please enter Number Only\n Try Again")
                continue

        with open("emp_end_yr.txt", 'w') as file:
            file.write(
                "ID,LastName,FirstName,JobCode,BasePay,Utilization,Evaluation/Sales,Bonus\n")
            for Id, item in self.employee_performances.items():
                row = Id+","+item['last_name']+","+item['first_name']+"," + \
                    item['job_code']+"," + \
                    str(item['base_pay'])+","+str(item['utilization'])+","
                if item['job_code'] == 'C':
                    row = row + str(item['Evaluation score']) + \
                        ","+str(item['Bonus']) + "\n"
                else:
                    row = row + str(item['sale'])+","+str(item['Bonus']) + "\n"

                file.write(row)
#         print("file saved Successfully")
        consultantbase_pay = []
        con_utilization = []
        con_evaluation = []
        con_bonus = []

        total_base_pay = []
        total_utilization = []
        total_sale = []
        total_bonus = []

        with open("emp_end_yr.txt", "r") as file:
            file_lines = file.readlines()

        for line in file_lines[1:]:
            Id, last_name, first_name, job_code, base_pay, utilization, evaluation_sales, bonus = line.strip().split(",")
            if int(bonus) == 0:
                continue
            else:
                if job_code == "C":
                    consultantbase_pay.append(int(base_pay))
                    con_utilization.append(int(utilization))
                    con_evaluation.append(int(evaluation_sales))
                    con_bonus.append(int(bonus))

                else:
                    total_base_pay.append(int(base_pay))
                    total_utilization.append(int(utilization))
                    total_sale.append(int(evaluation_sales))
                    total_bonus.append(int(bonus))

        self.performanceMatrix = {
            "Director": {
                "Mean": {
                    "Base_Pay": stats.mean(total_base_pay),
                    "Utilization": stats.mean(total_utilization),
                    "sale": stats.mean(total_sale),
                    "Bonus": stats.mean(total_bonus)
                },

                "Median": {
                    "Base_Pay": stats.median(total_base_pay),
                    "Utilization": stats.median(total_utilization),
                    "sale": stats.median(total_sale),
                    "Bonus": stats.median(total_bonus)
                },
                "Standard Deviation": {
                    "Base_Pay": stats.stdev(total_base_pay),
                    "Utilization": stats.stdev(total_utilization),
                    "sale": stats.stdev(total_sale),
                    "Bonus": stats.stdev(total_bonus)
                },
                "Minimum": {
                    "Base_Pay": np.min(total_base_pay),
                    "Utilization": np.min(total_utilization),
                    "sale": np.min(total_sale),
                    "Bonus": np.min(total_bonus)
                },
                "Maximum": {
                    "Base_Pay": np.max(total_base_pay),
                    "Utilization": np.max(total_utilization),
                    "sale": np.max(total_sale),
                    "Bonus": np.max(total_bonus)
                },
                "count": {
                    "Base_Pay": len(total_base_pay),
                    "Utilization": len(total_utilization),
                    "sale": len(total_sale),
                    "Bonus": len(total_bonus)
                }
            },

            "Consultants": {
                "Mean": {
                    "Base_Pay": stats.mean(consultantbase_pay),
                    "Utilization": stats.mean(con_utilization),
                    "evaluation": stats.mean(con_evaluation),
                    "Bonus": stats.mean(con_bonus)
                },

                "Median": {
                    "Base_Pay": stats.median(consultantbase_pay),
                    "Utilization": stats.median(con_utilization),
                    "evaluation": stats.median(con_evaluation),
                    "Bonus": stats.median(con_bonus)
                },
                "Standard Deviation": {
                    "Base_Pay": stats.stdev(consultantbase_pay),
                    "Utilization": stats.stdev(con_utilization),
                    "evaluation": stats.stdev(con_evaluation),
                    "Bonus": stats.stdev(con_bonus)
                },
                "Minimum": {
                    "Base_Pay": np.min(consultantbase_pay),
                    "Utilization": np.min(con_utilization),
                    "evaluation": np.min(con_evaluation),
                    "Bonus": np.min(con_bonus)
                },
                "Maximum": {
                    "Base_Pay": np.max(consultantbase_pay),
                    "Utilization": np.max(con_utilization),
                    "evaluation": np.max(con_evaluation),
                    "Bonus": np.max(con_bonus)
                },
                "count": {
                    "Base_Pay": len(consultantbase_pay),
                    "Utilization": len(con_utilization),
                    "evaluation": len(con_evaluation),
                    "Bonus": len(con_bonus)
                }
            }
        }


    def SearchEmployeeRecord(self):
        emp_id = input("Enter the Employee ID : ")
        if emp_id in self.employee_performances.keys():
            userType = ""
            print("ID: {}".format(emp_id))
            if self.employee_performances[emp_id]['job_code'] == 'C':
                userType = "Consultants"
                print("Consultant: {} {}".format(
                    self.employee_performances[emp_id]['first_name'], self.employee_performances[emp_id]['last_name']))
                print("Utilization: {}".format(
                    self.employee_performances[emp_id]['utilization']))
                print("Evaluation score: {}".format(
                    self.employee_performances[emp_id]['Evaluation score']))

            else:
                userType = "Director"
                print("Director: {} {}".format(
                    self.employee_performances[emp_id]['first_name'], self.employee_performances[emp_id]['last_name']))
                print("Utilization: {}".format(
                    self.employee_performances[emp_id]['utilization']))
                print("New Salary: ${}".format(0))
            print("Base pay: ${}".format(
                self.employee_performances[emp_id]['base_pay']))
            print("Bonus: ${}".format(
                self.employee_performances[emp_id]['Bonus']))
            if self.employee_performances[emp_id]['utilization'] == int(self.performanceMatrix[userType]["Maximum"]["Utilization"]):
                print("Maximum Utilization Score")

    def displaydescriptiveanalytics(self):
       
        print("Analysis of Consultants")
        print("---------------------------------------------------------------------------------------------------------")
        print("Mean    :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(
            self.performanceMatrix['Consultants']['Mean']['Base_Pay'], self.performanceMatrix['Consultants']['Mean']["Utilization"], self.performanceMatrix['Consultants']['Mean']['evaluation'], self.performanceMatrix['Consultants']['Mean']['Bonus']))
        print("Median  :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(self.performanceMatrix['Consultants']['Median']['Base_Pay'], self.performanceMatrix[
              'Consultants']['Median']["Utilization"], self.performanceMatrix['Consultants']['Median']['evaluation'], self.performanceMatrix['Consultants']['Median']['Bonus']))
        print("S.D.    :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(self.performanceMatrix['Consultants']['Standard Deviation']['Base_Pay'], self.performanceMatrix[
              'Consultants']['Standard Deviation']["Utilization"], self.performanceMatrix['Consultants']['Standard Deviation']['evaluation'], self.performanceMatrix['Consultants']['Standard Deviation']['Bonus']))
        print("Minimum :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(self.performanceMatrix['Consultants']['Minimum']['Base_Pay'], self.performanceMatrix[
              'Consultants']['Minimum']["Utilization"], self.performanceMatrix['Consultants']['Minimum']['evaluation'], self.performanceMatrix['Consultants']['Minimum']['Bonus']))
        print("Maximum :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(self.performanceMatrix['Consultants']['Maximum']['Base_Pay'], self.performanceMatrix[
              'Consultants']['Maximum']["Utilization"], self.performanceMatrix['Consultants']['Maximum']['evaluation'], self.performanceMatrix['Consultants']['Maximum']['Bonus']))
        print("count   :  Base Pay = {:.2f}\t Utilization = {:.2f}\t Evaluation = {:.2f}\t Bonus = {:.2f}".format(self.performanceMatrix['Consultants']['count']['Base_Pay'], self.performanceMatrix[
              'Consultants']['count']["Utilization"], self.performanceMatrix['Consultants']['count']['evaluation'], self.performanceMatrix['Consultants']['count']['Bonus']))

     
            
emp = EmployeePerformances()
emp.hours_worked()
emp.textual_evaluation()
emp.Finalized_rate()
choice = 0
while choice !=4 :
    print("\n\n")
    print("1.  Search Employee Details ")
    print("2.  Display Descriptive Analysis")

    try:
        choice = int(input("enter your choice : "))

        if choice == 1:
            emp.SearchEmployeeRecord()
     
        elif choice == 2 :
            emp.displaydescriptiveanalytics()
    
        else:
            print("Please Select Valid Options")
    except ValueError:
        print("enter only Numbers")
        
    
