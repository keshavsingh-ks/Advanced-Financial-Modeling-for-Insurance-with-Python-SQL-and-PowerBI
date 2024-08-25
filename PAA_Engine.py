import pandas as pd
import numpy as np

assumptions = pd.read_csv("Assumptions.csv")


class PAA:
    def discount(self, cf, interest):
        dcf = 0
        length = len(cf)
        interest = np.array(interest)
        cf = np.array(cf)
        for c in range(0, length):
            dcf = dcf + cf[c] * (1 + interest[c]) ** (-(c + 1))
        return dcf

    def __init__(self, assumptions):
        ## Initialise the statements
        self.Assumptions = assumptions.apply(pd.to_numeric)
        self.Contract_Boundary = len(assumptions)
        self.Expected_Cashflow = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "Premiums",
                "Acquisition Commission",
                "Renewal Commission",
                "Acquisition Expense Attributable",
                "Maintenance Expense Attributable",
                "Acquisition Expense Non-Attributable",
                "Maintenance Expense Non-Attributable",
                "Claims",
                "TOTAL NET CASH FLOWS",
            ],
        )
        self.Actual_Cashflow = self.Expected_Cashflow.copy()
        self.Liability_for_Remaining_Coverage = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "OPENING BALANCE",
                "Premium Cash Flow",
                "Acquisition Cost",
                "Acquisition Cost Amortisation",
                "Insurance Revenue",
                "CLOSING BALANCE",
            ],
        )
        self.Liability_for_Incurred_Claims = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "Estimates of the Present Value of Future Cash Flows OB",
                "Risk Adjustment for Non-Financial Risk OB",
                "OPENING BALANCE",
                "Estimates of the Present Value of Future Cash Flows EO",
                "Risk Adjustment for Non-Financial Risk EO",
                "INSURANCE SERVICE EXPENSE",
                "Estimates of the Present Value of Future Cash Flows AO",
                "CASH OUTFLOWS",
                "CLOSING BALANCE",
            ],
        )
        self.Insurance_Contract_Liability = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "Liability for Incurred Claims",
                "Liability for Remaining Coverage",
                "CLOSING BALANCE",
            ],
        )
        self.Expected_Risk_Adjustment_CF = pd.DataFrame(
            data=0, index=range(0, self.Contract_Boundary), columns=["Claims"]
        )
        self.Actual_Risk_Adjustment_CF = self.Expected_Risk_Adjustment_CF.copy()
        self.Coverage_Units_Recon = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=["OPENING", "Deaths", "Lapses", "CLOSING"],
        )

        self.Statement_of_Profit_or_Loss = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "Insurance Service Revenue",
                "Insurance Service Expense",
                "INSURANCE SERVICE RESULT",
                "OTHER EXPENSES",
                "Investment Income",
                "Insurance Financial Expense",
                "FINANCIAL GAIN/LOSS",
                "PROFIT OR LOSS",
            ],
        )
        self.rolling_sum = pd.DataFrame(
            data=0, index=range(0, self.Contract_Boundary), columns=["Coverage Units"]
        )

        # Coverage Units Recon
        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Coverage_Units_Recon.loc[i, "OPENING"] = self.Assumptions.loc[
                    i, "Policies Issued"
                ]
            else:
                self.Coverage_Units_Recon.loc[
                    i, "OPENING"
                ] = self.Coverage_Units_Recon.loc[i - 1, "CLOSING"]
            self.Coverage_Units_Recon.loc[i, "Deaths"] = (
                self.Assumptions.loc[i, "Mortality"]
                * self.Coverage_Units_Recon.loc[i, "OPENING"]
            )
            self.Coverage_Units_Recon.loc[i, "Lapses"] = (
                self.Assumptions.loc[i, "Lapse"]
                * self.Coverage_Units_Recon.loc[i, "OPENING"]
            )
            self.Coverage_Units_Recon.loc[i, "CLOSING"] = max(
                self.Coverage_Units_Recon.loc[i, "OPENING"]
                - self.Coverage_Units_Recon.loc[i, "Deaths"]
                - self.Coverage_Units_Recon.loc[i, "Lapses"],
                0,
            )

        for i in range(self.Contract_Boundary - 1, -1, -1):
            if i == (self.Contract_Boundary - 1):
                self.rolling_sum.loc[
                    i, "Coverage Units"
                ] = self.Coverage_Units_Recon.loc[i, "OPENING"]
            else:
                self.rolling_sum.loc[i, "Coverage Units"] = (
                    self.Coverage_Units_Recon.loc[i, "OPENING"]
                    + self.rolling_sum.loc[i + 1, "Coverage Units"]
                )

        # Expected Cashflows

        for i in range(0, self.Contract_Boundary):
            self.Expected_Cashflow.loc[i, "Premiums"] = self.Coverage_Units_Recon.loc[
                i, "OPENING"
            ] * (
                self.Assumptions.loc[i, "Premium Rate"]
                + self.Assumptions.loc[i, "Policy Fee"]
            )
            self.Expected_Cashflow.loc[i, "Claims"] = (
                -self.Coverage_Units_Recon.loc[i, "Deaths"]
                * self.Assumptions.loc[i, "Sum Assured"]
            )
            if i == 0:
                self.Expected_Cashflow.loc[i, "Acquisition Commission"] = (
                    -self.Expected_Cashflow.loc[i, "Premiums"]
                    * self.Assumptions.loc[i, "Commission"]
                )

            else:
                self.Expected_Cashflow.loc[i, "Renewal Commission"] = (
                    -self.Expected_Cashflow.loc[i, "Premiums"]
                    * self.Assumptions.loc[i, "Commission"]
                )
            self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * self.Assumptions.loc[i, "Acquisition Expense Attributable"]
            )
            self.Expected_Cashflow.loc[i, "Acquisition Expense Non-Attributable"] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * self.Assumptions.loc[i, "Acquisition Expense Non-Attributable"]
            )
            self.Expected_Cashflow.loc[i, "Maintenance Expense Attributable"] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * self.Assumptions.loc[i, "Maintenance Expense Attributable"]
            )
            self.Expected_Cashflow.loc[i, "Maintenance Expense Non-Attributable"] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * self.Assumptions.loc[i, "Maintenance Expense Non-Attributable"]
            )
            self.Expected_Cashflow.loc[i, "TOTAL NET CASH FLOWS"] = (
                self.Expected_Cashflow.loc[i, "Premiums"]
                + self.Expected_Cashflow.loc[i, "Claims"]
                + self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Non-Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
                + self.Expected_Cashflow.loc[i, "Maintenance Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Maintenance Expense Non-Attributable"]
            )

        # Actual Cashflow = Expected Cashflow

        self.Actual_Cashflow = self.Expected_Cashflow.copy()

        # Expected Risk Adjustment

        for i in range(0, self.Contract_Boundary):
            self.Expected_Risk_Adjustment_CF.loc[i, "Claims"] = (
                self.Assumptions.loc[i, "Non-Financial Risk Adjustment"]
                * self.Expected_Cashflow.loc[i, "Claims"]
            )

            # Actual Risk Adjustment Cashflow = Expected Risk Adjustment Cashflow

        self.Actual_Risk_Adjustment_CF = self.Expected_Risk_Adjustment_CF.copy()

        # Present Value of Premiums

        self.EPV_Premiums = self.Expected_Cashflow.loc[:, "Premiums"].sum()

        # Present Value of Claims

        self.EPV_Claims = self.Expected_Cashflow.loc[:, "Claims"].sum()

        # Liability for Remaining Coverage

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Liability_for_Remaining_Coverage.loc[i, "OPENING BALANCE"] = 0
                self.Liability_for_Remaining_Coverage.loc[i, "Acquisition Cost"] = (
                    -self.Coverage_Units_Recon.loc[i, "OPENING"]
                    * self.Assumptions.loc[i, "Acquisition Expense Attributable"]
                )
            else:
                self.Liability_for_Remaining_Coverage.loc[
                    i, "Acquisition Cost Amortisation"
                ] = (
                    (-1)
                    * self.Liability_for_Remaining_Coverage.loc[0, "Acquisition Cost"]
                    / (self.Contract_Boundary - 1)
                )
                self.Liability_for_Remaining_Coverage.loc[
                    i, "OPENING BALANCE"
                ] = self.Liability_for_Remaining_Coverage.loc[i - 1, "CLOSING BALANCE"]
            self.Liability_for_Remaining_Coverage.loc[
                i, "Premium Cash Flow"
            ] = self.Expected_Cashflow.loc[i, "Premiums"]
            self.Liability_for_Remaining_Coverage.loc[
                i, "Insurance Revenue"
            ] = -self.EPV_Premiums / (self.Contract_Boundary)
            self.Liability_for_Remaining_Coverage.loc[i, "CLOSING BALANCE"] = (
                self.Liability_for_Remaining_Coverage.loc[i, "OPENING BALANCE"]
                + self.Liability_for_Remaining_Coverage.loc[i, "Acquisition Cost"]
                + self.Liability_for_Remaining_Coverage.loc[
                    i, "Acquisition Cost Amortisation"
                ]
                + self.Liability_for_Remaining_Coverage.loc[i, "Premium Cash Flow"]
                + self.Liability_for_Remaining_Coverage.loc[i, "Insurance Revenue"]
            )

        # Liability for Incurred Claims

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Liability_for_Incurred_Claims.loc[
                    i, "Estimates of the Present Value of Future Cash Flows OB"
                ] = 0
                self.Liability_for_Incurred_Claims.loc[
                    i, "Risk Adjustment for Non-Financial Risk OB"
                ] = 0
                self.Liability_for_Incurred_Claims.loc[
                    i, "Risk Adjustment for Non-Financial Risk EO"
                ] = (
                    self.EPV_Premiums
                    * self.Assumptions.loc[i, "Non-Financial Risk Adjustment"]
                ) + self.EPV_Claims
            else:
                self.Liability_for_Incurred_Claims.loc[
                    i, "Estimates of the Present Value of Future Cash Flows OB"
                ] = (
                    self.Liability_for_Incurred_Claims.loc[
                        i - 1, "Estimates of the Present Value of Future Cash Flows OB"
                    ]
                    + self.Liability_for_Incurred_Claims.loc[
                        i - 1, "Estimates of the Present Value of Future Cash Flows EO"
                    ]
                    + self.Liability_for_Incurred_Claims.loc[
                        i - 1, "Estimates of the Present Value of Future Cash Flows AO"
                    ]
                )
                self.Liability_for_Incurred_Claims.loc[
                    i, "Risk Adjustment for Non-Financial Risk OB"
                ] = (
                    self.Liability_for_Incurred_Claims.loc[
                        i - 1, "Risk Adjustment for Non-Financial Risk OB"
                    ]
                    + self.Liability_for_Incurred_Claims.loc[
                        i - 1, "Risk Adjustment for Non-Financial Risk EO"
                    ]
                )
            self.Liability_for_Incurred_Claims.loc[i, "OPENING BALANCE"] = (
                self.Liability_for_Incurred_Claims.loc[
                    i, "Estimates of the Present Value of Future Cash Flows OB"
                ]
                + self.Liability_for_Incurred_Claims.loc[
                    i, "Risk Adjustment for Non-Financial Risk OB"
                ]
            )
            self.Liability_for_Incurred_Claims.loc[
                i, "Estimates of the Present Value of Future Cash Flows EO"
            ] = -(
                self.Expected_Cashflow.loc[i, "Claims"]
                + self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
                + self.Expected_Cashflow.loc[i, "Maintenance Expense Attributable"]
            )
            self.Liability_for_Incurred_Claims.loc[
                i, "Risk Adjustment for Non-Financial Risk EO"
            ] = (
                (-1)
                * self.Liability_for_Incurred_Claims.loc[
                    0, "Risk Adjustment for Non-Financial Risk EO"
                ]
                / (self.Contract_Boundary - 1)
            )
            self.Liability_for_Incurred_Claims.loc[i, "INSURANCE SERVICE EXPENSE"] = (
                self.Liability_for_Incurred_Claims.loc[
                    i, "Estimates of the Present Value of Future Cash Flows EO"
                ]
                + self.Liability_for_Incurred_Claims.loc[
                    i, "Risk Adjustment for Non-Financial Risk EO"
                ]
            )
            self.Liability_for_Incurred_Claims.loc[
                i, "Estimates of the Present Value of Future Cash Flows AO"
            ] = (
                self.Actual_Cashflow.loc[i, "Claims"]
                + self.Actual_Cashflow.loc[i, "Acquisition Commission"]
                + self.Actual_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Actual_Cashflow.loc[i, "Renewal Commission"]
                + self.Actual_Cashflow.loc[i, "Maintenance Expense Attributable"]
            )
            self.Liability_for_Incurred_Claims.loc[
                i, "CASH OUTFLOWS"
            ] = self.Liability_for_Incurred_Claims.loc[
                i, "Estimates of the Present Value of Future Cash Flows AO"
            ]
            self.Liability_for_Incurred_Claims.loc[i, "CLOSING BALANCE"] = (
                self.Liability_for_Incurred_Claims.loc[i, "OPENING BALANCE"]
                + self.Liability_for_Incurred_Claims.loc[i, "INSURANCE SERVICE EXPENSE"]
                + self.Liability_for_Incurred_Claims.loc[i, "CASH OUTFLOWS"]
            )

        # Insurance Contract Liability
        for i in range(0, self.Contract_Boundary):
            self.Insurance_Contract_Liability.loc[
                i, "Liability for Incurred Claims"
            ] = self.Liability_for_Incurred_Claims.loc[i, "CLOSING BALANCE"]
            self.Insurance_Contract_Liability.loc[
                i, "Liability for Remaining Coverage"
            ] = self.Liability_for_Remaining_Coverage.loc[i, "CLOSING BALANCE"]
            self.Insurance_Contract_Liability.loc[i, "CLOSING BALANCE"] = (
                self.Insurance_Contract_Liability.loc[
                    i, "Liability for Incurred Claims"
                ]
                + self.Insurance_Contract_Liability.loc[
                    i, "Liability for Remaining Coverage"
                ]
            )

        # Statement of Profit and Loss

        for i in range(0, self.Contract_Boundary):
            self.Statement_of_Profit_or_Loss.loc[
                i, "Insurance Service Revenue"
            ] = -self.Liability_for_Remaining_Coverage.loc[i, "Insurance Revenue"]
            self.Statement_of_Profit_or_Loss.loc[
                i, "Insurance Service Expense"
            ] = -self.Liability_for_Incurred_Claims.loc[i, "INSURANCE SERVICE EXPENSE"]
            self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE RESULT"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "Insurance Service Revenue"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Insurance Service Expense"]
            )
            self.Statement_of_Profit_or_Loss.loc[i, "OTHER EXPENSES"] = (
                self.Actual_Cashflow.loc[i, "Acquisition Expense Non-Attributable"]
                + self.Actual_Cashflow.loc[i, "Maintenance Expense Non-Attributable"]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Investment Income"
            ] = 0  # self.Assumptions.loc[i, "Asset Earned Rate"]*(self.Reconciliation_of_Total_Contract_Liability.loc[i, "Changes Related to Future Service: New Business"]+self.Reconciliation_of_Total_Contract_Liability.loc[i, "OPENING"]+self.Expected_Cashflow.loc[i, "Premiums"]+self.Expected_Cashflow.loc[i, "Acquisition Commission"]+self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]+self.Expected_Cashflow.loc[i, "Renewal Commission"])
            self.Statement_of_Profit_or_Loss.loc[
                i, "Insurance Financial Expense"
            ] = 0  # -self.Reconciliation_of_Total_Contract_Liability.loc[i, "Insurance Service Expense"]
            self.Statement_of_Profit_or_Loss.loc[i, "FINANCIAL GAIN/LOSS"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "Investment Income"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Insurance Financial Expense"]
            )
            self.Statement_of_Profit_or_Loss.loc[i, "PROFIT OR LOSS"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE RESULT"]
                + self.Statement_of_Profit_or_Loss.loc[i, "OTHER EXPENSES"]
                + self.Statement_of_Profit_or_Loss.loc[i, "FINANCIAL GAIN/LOSS"]
            )

    def Expected_Cashflow_Statement(self):
        return round(self.Expected_Cashflow).to_csv("Expected_Cashflow_Statement.csv")

    def Actual_Cashflow_Statement(self):
        return round(self.Actual_Cashflow).to_csv("Actual_Cashflow_Statement.csv")

    def Coverage_Units_Recon_Statement(self):
        return round(self.Coverage_Units_Recon).to_csv(
            "Coverage_Units_Recon_Statement.csv"
        )

    def Expected_Risk_Adjustment_Statement(self):
        return round(self.Expected_Risk_Adjustment_CF).to_csv(
            "Expected_Risk_Adjustment.csv"
        )

    def Actual_Risk_Adjustment_Statement(self):
        return round(self.Actual_Risk_Adjustment_CF).to_csv(
            "Actual_Risk_Adjustment_Statement.csv"
        )

    def Liability_for_Remaining_Coverage_Statement(self):
        return round(self.Liability_for_Remaining_Coverage).to_csv(
            "Liability_for_Remaining_Coverage.csv"
        )

    def Liability_for_Incurred_Claims_Statement(self):
        return round(self.Liability_for_Incurred_Claims).to_csv(
            "Liability_for_Incurred_Claims.csv"
        )

    def Insurance_Contract_Liability_Statement(self):
        return round(self.Insurance_Contract_Liability).to_csv(
            "Insurance_Contract_Liability.csv"
        )

    def Profit_or_Loss_Statement(self):
        return round(self.Statement_of_Profit_or_Loss).to_csv(
            "Profit_or_Loss_Statement.csv"
        )

    def All_Statements(self):
        return (
            round(self.Expected_Cashflow).to_csv("Expected_Cashflow_Statement.csv"),
            round(self.Actual_Cashflow).to_csv("Actual_Cashflow_Statement.csv"),
            round(self.Coverage_Units_Recon).to_csv(
                "Coverage_Units_Recon_Statement.csv"
            ),
            round(self.Expected_Risk_Adjustment_CF).to_csv(
                "Expected_Risk_Adjustment.csv"
            ),
            round(self.Actual_Risk_Adjustment_CF).to_csv(
                "Actual_Risk_Adjustment_Statement.csv"
            ),
            round(self.Liability_for_Remaining_Coverage).to_csv(
                "Liability_for_Remaining_Coverage.csv"
            ),
            round(self.Liability_for_Incurred_Claims).to_csv(
                "Liability_for_Incurred_Claims.csv"
            ),
            round(self.Insurance_Contract_Liability).to_csv(
                "Insurance_Contract_Liability.csv"
            ),
            round(self.Statement_of_Profit_or_Loss).to_csv(
                "Profit_or_Loss_Statement.csv"
            ),
        )

    def Chart_of_Accounts(self, year, drop_zeros):
        GL = pd.DataFrame()

        def add_account(GL, account, title, drop):
            k = len(GL)
            for i in range(len(account.columns)):
                if not str(account.columns[i]).isupper():
                    GL.loc[i + k, "Period"] = int(year)
                    if "PL" in str(title):
                        GL.loc[i + k, "Statement"] = "PL"
                        if str(account.columns[i]) in ["Insurance Service Revenue"]:
                            GL.loc[i + k, "Group"] = "PLIR"
                        elif str(account.columns[i]) in ["Insurance Service Expense"]:
                            GL.loc[i + k, "Group"] = "PLIE"
                        else:
                            GL.loc[i + k, "Group"] = "PLFGL"
                    else:
                        GL.loc[i + k, "Statement"] = "BS"
                        GL.loc[i + k, "Group"] = str(title)
                    GL.loc[i + k, "Account Name"] = str(account.columns[i])
                    GL.loc[i + k, "Amount"] = account.iloc[year, i]
                elif str(account.columns[i]) in ["OTHER EXPENSES"]:
                    GL.loc[i + k, "Period"] = int(year)
                    GL.loc[i + k, "Statement"] = "PL"
                    GL.loc[i + k, "Group"] = "PLOE"
                    GL.loc[i + k, "Account Name"] = "Other Expenses"
                    GL.loc[i + k, "Amount"] = account.iloc[year, i]

            if drop is True:
                GL = GL[GL.Amount != 0].reset_index(drop=True)
            return GL

        list_of_accounts = [
            self.Expected_Cashflow,
            self.Actual_Cashflow,
            self.Expected_Risk_Adjustment_CF,
            self.Actual_Risk_Adjustment_CF,
            self.Liability_for_Remaining_Coverage,
            self.Liability_for_Incurred_Claims,
            self.Insurance_Contract_Liability,
            self.Statement_of_Profit_or_Loss,
        ]
        list_of_account_abv = ["ECF", "ACF", "ERA", "ARA", "LRC", "LIC", "ICL", "PL"]

        for accounts, name in zip(list_of_accounts, list_of_account_abv):
            GL = add_account(GL, accounts, name, drop_zeros)

        return round(GL).to_csv(str("Chart of Accounts - PAA_" + str(year) + ".csv"))


assumptions = pd.read_csv("data/Assumptions.csv")
ifrs = PAA(assumptions)

for i in range(len(assumptions)):
    ifrs.Chart_of_Accounts(i, True)
ifrs.All_Statements()
