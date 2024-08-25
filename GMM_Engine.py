import pandas as pd
import numpy as np
from functools import reduce


class GMM:
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
        self.Expected_Risk_Adjustment_CF = pd.DataFrame(
            data=0, index=range(0, self.Contract_Boundary), columns=["Claims"]
        )
        self.Actual_Risk_Adjustment_CF = self.Expected_Risk_Adjustment_CF.copy()
        self.Coverage_Units_Recon = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=["OPENING", "Deaths", "Lapses", "CLOSING"],
        )
        self.Liability_on_Initial_Recognition = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "PV Premiums",
                "PV Renewal Commission",
                "PV Maintenance Expense Attributable",
                "PV Claims",
                "PV Attributable Acquisition CFs",
                "PV Risk Adjustment CFs",
                "TOTAL FULFILLMENT CFs",
                "CSM at Initial Recognition",
                "LIABILITY ON INITIAL RECOGNITION",
            ],
        )
        self.Reconciliation_of_Best_Estimate_Liability = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "OPENING",
                "Changes Related to Future Service: New Business",
                "Changes Related to Future Service: Assumptions",
                "Expected Cash Inflows",
                "Expected Cash Outflows",
                "Insurance Service Expense",
                "Changes Related to Current Service: Experience",
                "Changes Related to Current Service: Release",
                "CLOSING",
            ],
        )
        self.Reconciliation_of_Risk_Adjustment = (
            self.Reconciliation_of_Best_Estimate_Liability.copy()
        )
        self.Reconciliation_of_Total_Contract_Liability = (
            self.Reconciliation_of_Best_Estimate_Liability.copy()
        )
        self.Reconciliation_of_Contractual_Service_Margin = (
            self.Reconciliation_of_Best_Estimate_Liability.copy()
        )
        self.Reconciliation_of_Acquisition_Expense_Amortisation = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "OPENING",
                "New Acquisition Expense",
                "Accretion of Interest",
                "Amortised Expense",
                "CLOSING",
            ],
        )
        self.Statement_of_Profit_or_Loss = pd.DataFrame(
            data=0,
            index=range(0, self.Contract_Boundary),
            columns=[
                "Release of CSM",
                "Release of Risk Adjustment",
                "Expected Claims",
                "Expected Expenses",
                "Recovery of Acquisition Cash Flows",
                "INSURANCE SERVICE REVENUE",
                "Claims Incurred",
                "Expenses Incurred",
                "Amortisation of Acquisition Cash Flows",
                "INSURANCE SERVICE EXPENSES",
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

        # Liability on Initial Recognition

        for i in range(0, self.Contract_Boundary):
            if i < (self.Contract_Boundary - 1):
                self.Liability_on_Initial_Recognition.loc[
                    i, "PV Premiums"
                ] = self.Expected_Cashflow.loc[i, "Premiums"] + self.discount(
                    self.Expected_Cashflow.loc[i + 1 :, "Premiums"],
                    self.Assumptions.loc[i + 1 :, "Discount Rate at Issue"],
                )
                self.Liability_on_Initial_Recognition.loc[
                    i, "PV Renewal Commission"
                ] = self.Expected_Cashflow.loc[i, "Renewal Commission"] + self.discount(
                    self.Expected_Cashflow.loc[i + 1 :, "Renewal Commission"],
                    self.Assumptions.loc[i + 1 :, "Discount Rate at Issue"],
                )
            else:
                self.Liability_on_Initial_Recognition.loc[
                    i, "PV Premiums"
                ] = self.Expected_Cashflow.loc[i, "Premiums"]
                self.Liability_on_Initial_Recognition.loc[
                    i, "PV Renewal Commission"
                ] = self.Expected_Cashflow.loc[i, "Renewal Commission"]
            self.Liability_on_Initial_Recognition.loc[
                i, "PV Maintenance Expense Attributable"
            ] = self.discount(
                self.Expected_Cashflow.loc[i:, "Maintenance Expense Attributable"],
                self.Assumptions.loc[i:, "Discount Rate at Issue"],
            )
            self.Liability_on_Initial_Recognition.loc[i, "PV Claims"] = self.discount(
                self.Expected_Cashflow.loc[i:, "Claims"],
                self.Assumptions.loc[i:, "Discount Rate at Issue"],
            )
            self.Liability_on_Initial_Recognition.loc[
                i, "PV Attributable Acquisition CFs"
            ] = (
                self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
            )
            self.Liability_on_Initial_Recognition.loc[
                i, "PV Risk Adjustment CFs"
            ] = self.discount(
                self.Expected_Risk_Adjustment_CF.loc[i:, "Claims"],
                self.Assumptions.loc[i:, "Discount Rate at Issue"],
            )
            self.Liability_on_Initial_Recognition.loc[i, "TOTAL FULFILLMENT CFs"] = (
                self.Liability_on_Initial_Recognition.loc[i, "PV Premiums"]
                + self.Liability_on_Initial_Recognition.loc[i, "PV Renewal Commission"]
                + self.Liability_on_Initial_Recognition.loc[
                    i, "PV Maintenance Expense Attributable"
                ]
                + self.Liability_on_Initial_Recognition.loc[i, "PV Claims"]
                + self.Liability_on_Initial_Recognition.loc[
                    i, "PV Attributable Acquisition CFs"
                ]
                + self.Liability_on_Initial_Recognition.loc[i, "PV Risk Adjustment CFs"]
            )
            self.Liability_on_Initial_Recognition.loc[
                0, "CSM at Initial Recognition"
            ] = max(
                0, self.Liability_on_Initial_Recognition.loc[0, "TOTAL FULFILLMENT CFs"]
            )
            self.Liability_on_Initial_Recognition.loc[
                i, "LIABILITY ON INITIAL RECOGNITION"
            ] = (
                self.Liability_on_Initial_Recognition.loc[i, "TOTAL FULFILLMENT CFs"]
                - self.Liability_on_Initial_Recognition.loc[
                    i, "CSM at Initial Recognition"
                ]
            )

        # Reconciliation of Best Estimate Liability

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Future Service: New Business"
                ] = -(
                    self.Liability_on_Initial_Recognition.loc[0, "PV Premiums"]
                    + self.Liability_on_Initial_Recognition.loc[
                        0, "PV Renewal Commission"
                    ]
                    + self.Liability_on_Initial_Recognition.loc[
                        0, "PV Maintenance Expense Attributable"
                    ]
                    + self.Liability_on_Initial_Recognition.loc[0, "PV Claims"]
                    + self.Liability_on_Initial_Recognition.loc[
                        0, "PV Attributable Acquisition CFs"
                    ]
                )
            else:
                self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "OPENING"
                ] = self.Reconciliation_of_Best_Estimate_Liability.loc[i - 1, "CLOSING"]
            self.Reconciliation_of_Best_Estimate_Liability.loc[
                i, "Expected Cash Inflows"
            ] = self.Expected_Cashflow.loc[i, "Premiums"]
            self.Reconciliation_of_Best_Estimate_Liability.loc[
                i, "Expected Cash Outflows"
            ] = (
                self.Expected_Cashflow.loc[i, "Claims"]
                + self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
                + self.Expected_Cashflow.loc[i, "Maintenance Expense Attributable"]
            )
            self.Reconciliation_of_Best_Estimate_Liability.loc[
                i, "Insurance Service Expense"
            ] = self.Assumptions.loc[i, "Discount Rate at Issue"] * (
                self.Reconciliation_of_Best_Estimate_Liability.loc[i, "OPENING"]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
                + self.Expected_Cashflow.loc[i, "Premiums"]
                + self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
            )
            self.Reconciliation_of_Best_Estimate_Liability.loc[i, "CLOSING"] = (
                self.Reconciliation_of_Best_Estimate_Liability.loc[i, "OPENING"]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Future Service: Assumptions"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Expected Cash Inflows"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Expected Cash Outflows"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Insurance Service Expense"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Current Service: Experience"
                ]
                + self.Reconciliation_of_Best_Estimate_Liability.loc[
                    i, "Changes Related to Current Service: Release"
                ]
            )

        # Reconciliation of Risk Adjustment

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Future Service: New Business"
                ] = -self.Liability_on_Initial_Recognition.loc[
                    i, "PV Risk Adjustment CFs"
                ]
            else:
                self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "OPENING"
                ] = self.Reconciliation_of_Risk_Adjustment.loc[i - 1, "CLOSING"]
            self.Reconciliation_of_Risk_Adjustment.loc[
                i, "Insurance Service Expense"
            ] = self.Assumptions.loc[i, "Discount Rate at Issue"] * (
                self.Reconciliation_of_Risk_Adjustment.loc[i, "OPENING"]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
            )
            self.Reconciliation_of_Risk_Adjustment.loc[
                i, "Changes Related to Current Service: Release"
            ] = self.Expected_Risk_Adjustment_CF.loc[i, "Claims"]
            self.Reconciliation_of_Risk_Adjustment.loc[i, "CLOSING"] = (
                self.Reconciliation_of_Risk_Adjustment.loc[i, "OPENING"]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Future Service: Assumptions"
                ]
                + self.Reconciliation_of_Risk_Adjustment.loc[i, "Expected Cash Inflows"]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Expected Cash Outflows"
                ]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Insurance Service Expense"
                ]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Current Service: Experience"
                ]
                + self.Reconciliation_of_Risk_Adjustment.loc[
                    i, "Changes Related to Current Service: Release"
                ]
            )

        # Reconciliation of CSM

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Reconciliation_of_Contractual_Service_Margin.loc[
                    0, "Changes Related to Future Service: New Business"
                ] = self.Liability_on_Initial_Recognition.loc[
                    0, "CSM at Initial Recognition"
                ]
            else:
                self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "OPENING"
                ] = self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i - 1, "CLOSING"
                ]
            self.Reconciliation_of_Contractual_Service_Margin.loc[
                i, "Insurance Service Expense"
            ] = self.Assumptions.loc[i, "Discount Rate at Issue"] * (
                self.Reconciliation_of_Contractual_Service_Margin.loc[i, "OPENING"]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
            )
            self.Reconciliation_of_Contractual_Service_Margin.loc[
                i, "Changes Related to Current Service: Release"
            ] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * (
                    self.Reconciliation_of_Contractual_Service_Margin.loc[i, "OPENING"]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Changes Related to Future Service: New Business"
                    ]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Changes Related to Future Service: Assumptions"
                    ]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Expected Cash Inflows"
                    ]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Expected Cash Outflows"
                    ]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Insurance Service Expense"
                    ]
                    + self.Reconciliation_of_Contractual_Service_Margin.loc[
                        i, "Changes Related to Current Service: Experience"
                    ]
                )
                / self.rolling_sum.loc[i, "Coverage Units"]
            )
            self.Reconciliation_of_Contractual_Service_Margin.loc[i, "CLOSING"] = (
                self.Reconciliation_of_Contractual_Service_Margin.loc[i, "OPENING"]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Changes Related to Future Service: Assumptions"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Expected Cash Inflows"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Expected Cash Outflows"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Insurance Service Expense"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Changes Related to Current Service: Experience"
                ]
                + self.Reconciliation_of_Contractual_Service_Margin.loc[
                    i, "Changes Related to Current Service: Release"
                ]
            )

            # Reconciliation of Total Contract Liability

        self.Reconciliation_of_Total_Contract_Liability = reduce(
            lambda a, b: a.add(b, fill_value=0),
            [
                self.Reconciliation_of_Contractual_Service_Margin,
                self.Reconciliation_of_Risk_Adjustment,
                self.Reconciliation_of_Best_Estimate_Liability,
            ],
        )

        # self.Reconciliation_of_Total_Contract_Liability = self.Reconciliation_of_Best_Estimate_Liability+self.Reconciliation_of_Risk_Adjustment+self.Reconciliation_of_Contractual_Service_Margin

        # Reconciliation of Acquisition Cost Amortisation

        for i in range(0, self.Contract_Boundary):
            if i == 0:
                self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "New Acquisition Expense"
                ] = -(
                    self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                    + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                )
            else:
                self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "OPENING"
                ] = self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i - 1, "CLOSING"
                ]
            self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                i, "Accretion of Interest"
            ] = self.Assumptions.loc[i, "Discount Rate at Issue"] * (
                self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "OPENING"
                ]
                + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "New Acquisition Expense"
                ]
            )
            self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                i, "Amortised Expense"
            ] = (
                -self.Coverage_Units_Recon.loc[i, "OPENING"]
                * (
                    self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                        i, "OPENING"
                    ]
                    + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                        i, "New Acquisition Expense"
                    ]
                    + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                        i, "Accretion of Interest"
                    ]
                )
                / self.rolling_sum.loc[i, "Coverage Units"]
            )
            self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                i, "CLOSING"
            ] = (
                self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "OPENING"
                ]
                + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "New Acquisition Expense"
                ]
                + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "Accretion of Interest"
                ]
                + self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                    i, "Amortised Expense"
                ]
            )

        # Statemoent of Profit and Loss

        for i in range(0, self.Contract_Boundary):
            self.Statement_of_Profit_or_Loss.loc[
                i, "Release of CSM"
            ] = -self.Reconciliation_of_Contractual_Service_Margin.loc[
                i, "Changes Related to Current Service: Release"
            ]
            self.Statement_of_Profit_or_Loss.loc[
                i, "Release of Risk Adjustment"
            ] = -self.Reconciliation_of_Risk_Adjustment.loc[
                i, "Changes Related to Current Service: Release"
            ]
            self.Statement_of_Profit_or_Loss.loc[
                i, "Expected Claims"
            ] = -self.Expected_Cashflow.loc[i, "Claims"]
            self.Statement_of_Profit_or_Loss.loc[i, "Expected Expenses"] = -(
                self.Expected_Cashflow.loc[i, "Maintenance Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Recovery of Acquisition Cash Flows"
            ] = -self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                i, "Amortised Expense"
            ]
            self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE REVENUE"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "Release of CSM"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Release of Risk Adjustment"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Expected Claims"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Expected Expenses"]
                + self.Statement_of_Profit_or_Loss.loc[
                    i, "Recovery of Acquisition Cash Flows"
                ]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Claims Incurred"
            ] = self.Actual_Cashflow.loc[i, "Claims"]
            self.Statement_of_Profit_or_Loss.loc[i, "Expenses Incurred"] = (
                self.Actual_Cashflow.loc[i, "Renewal Commission"]
                + self.Actual_Cashflow.loc[i, "Maintenance Expense Attributable"]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Amortisation of Acquisition Cash Flows"
            ] = self.Reconciliation_of_Acquisition_Expense_Amortisation.loc[
                i, "Amortised Expense"
            ]
            self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE EXPENSES"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "Claims Incurred"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Expenses Incurred"]
                + self.Statement_of_Profit_or_Loss.loc[
                    i, "Amortisation of Acquisition Cash Flows"
                ]
            )
            self.Statement_of_Profit_or_Loss.loc[i, "OTHER EXPENSES"] = (
                self.Actual_Cashflow.loc[i, "Acquisition Expense Non-Attributable"]
                + self.Actual_Cashflow.loc[i, "Maintenance Expense Non-Attributable"]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Investment Income"
            ] = self.Assumptions.loc[i, "Asset Earned Rate"] * (
                self.Reconciliation_of_Total_Contract_Liability.loc[
                    i, "Changes Related to Future Service: New Business"
                ]
                + self.Reconciliation_of_Total_Contract_Liability.loc[i, "OPENING"]
                + self.Expected_Cashflow.loc[i, "Premiums"]
                + self.Expected_Cashflow.loc[i, "Acquisition Commission"]
                + self.Expected_Cashflow.loc[i, "Acquisition Expense Attributable"]
                + self.Expected_Cashflow.loc[i, "Renewal Commission"]
            )
            self.Statement_of_Profit_or_Loss.loc[
                i, "Insurance Financial Expense"
            ] = -self.Reconciliation_of_Total_Contract_Liability.loc[
                i, "Insurance Service Expense"
            ]
            self.Statement_of_Profit_or_Loss.loc[i, "FINANCIAL GAIN/LOSS"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "Investment Income"]
                + self.Statement_of_Profit_or_Loss.loc[i, "Insurance Financial Expense"]
            )
            self.Statement_of_Profit_or_Loss.loc[i, "PROFIT OR LOSS"] = (
                self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE REVENUE"]
                + self.Statement_of_Profit_or_Loss.loc[i, "INSURANCE SERVICE EXPENSES"]
                + self.Statement_of_Profit_or_Loss.loc[i, "OTHER EXPENSES"]
                + self.Statement_of_Profit_or_Loss.loc[i, "FINANCIAL GAIN/LOSS"]
            )

    def Liability_on_Initial_Recognition_Statement(self):
        return round(self.Liability_on_Initial_Recognition).to_csv(
            "Liability_on_Initial_Recognition.csv"
        )

    def Expected_Cashflow_Statement(self):
        return round(self.Expected_Cashflow).to_csv("Expected_Cashflow_Statement.csv")

    def Actual_Cashflow_Statement(self):
        return round(self.Actual_Cashflow).to_csv("Actual_Cashflow_Statement.csv")

    def Expected_Risk_Adjustment_Statement(self):
        return round(self.Expected_Risk_Adjustment_CF).to_csv(
            "Expected_Risk_Adjustemt.csv"
        )

    def Actual_Risk_Adjustment_Statement(self):
        return round(self.Actual_Risk_Adjustment_CF).to_csv(
            "Actual_Risk_Adjustment_Statement.csv"
        )

    def Coverage_Units_Recon_Statement(self):
        return round(self.Coverage_Units_Recon).to_csv(
            "Coverage_Units_Recon_Statement.csv"
        )

    def Reconciliation_of_Best_Estimate_Liability_Statement(self):
        return round(self.Reconciliation_of_Best_Estimate_Liability).to_csv(
            "Reconciliation_of_Best_Estimate_Liability_Statement.csv"
        )

    def Reconciliation_of_Contractual_Service_Margin_Statement(self):
        return round(self.Reconciliation_of_Contractual_Service_Margin).to_csv(
            "Reconciliation_of_Contractual_Service_Margin_Statement.csv"
        )

    def Reconciliation_of_Total_Contract_Liability_Statement(self):
        return round(self.Reconciliation_of_Total_Contract_Liability).to_csv(
            "Reconciliation_of_Total_Contract_Liability_Statement.csv"
        )

    def Reconciliation_of_Risk_Adjustment_Statement(self):
        return round(self.Reconciliation_of_Risk_Adjustment).to_csv(
            "Reconciliation_of_Risk_Adjustment_Statement.csv"
        )

    def Reconciliation_of_Acquisition_Expense_Amortisation_Statement(self):
        return round(self.Reconciliation_of_Acquisition_Expense_Amortisation).to_csv(
            "Reconciliation_of_Acquisition_Expense_Amortisation_Statement.csv"
        )

    def Profit_or_Loss_Statement(self):
        return round(self.Statement_of_Profit_or_Loss).to_csv(
            "Profit_or_Loss_Statement.csv"
        )

    def All_Statements(self):
        return (
            round(self.Liability_on_Initial_Recognition).to_csv(
                "Liability_on_Initial_Recognition.csv"
            ),
            round(self.Expected_Cashflow).to_csv("Expected_Cashflow_Statement.csv"),
            round(self.Actual_Cashflow).to_csv("Actual_Cashflow_Statement.csv"),
            round(self.Expected_Risk_Adjustment_CF).to_csv(
                "Expected_Risk_Adjustemt.csv"
            ),
            round(self.Actual_Risk_Adjustment_CF).to_csv(
                "Actual_Risk_Adjustment_Statement.csv"
            ),
            round(self.Coverage_Units_Recon).to_csv(
                "Coverage_Units_Recon_Statement.csv"
            ),
            round(self.Reconciliation_of_Best_Estimate_Liability).to_csv(
                "Reconciliation_of_Best_Estimate_Liability_Statement.csv"
            ),
            round(self.Reconciliation_of_Contractual_Service_Margin).to_csv(
                "Reconciliation_of_Contractual_Service_Margin_Statement.csv"
            ),
            round(self.Reconciliation_of_Total_Contract_Liability).to_csv(
                "Reconciliation_of_Total_Contract_Liability_Statement.csv"
            ),
            round(self.Reconciliation_of_Risk_Adjustment).to_csv(
                "Reconciliation_of_Risk_Adjustment_Statement.csv"
            ),
            round(self.Reconciliation_of_Acquisition_Expense_Amortisation).to_csv(
                "Reconciliation_of_Acquisition_Expense_Amortisation_Statement.csv"
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
                        if str(account.columns[i]) in [
                            "Release of CSM",
                            "Release of Risk Adjustment",
                            "Expected Claims",
                            "Expected Expenses",
                            "Recovery of Acquisition Cash Flows",
                        ]:
                            GL.loc[i + k, "Group"] = "PLIR"
                        elif str(account.columns[i]) in [
                            "Claims Incurred",
                            "Expenses Incurred",
                        ]:
                            GL.loc[i + k, "Group"] = "PLIE"
                        elif str(account.columns[i]) in [
                            "Amortisation of Acquisition Cash Flows"
                        ]:
                            GL.loc[i + k, "Group"] = "PLOE"
                        else:
                            GL.loc[i + k, "Group"] = "PLFGL"
                    else:
                        GL.loc[i + k, "Statement"] = "BS"
                        GL.loc[i + k, "Group"] = str(title)
                    GL.loc[i + k, "Account Name"] = str(account.columns[i])
                    GL.loc[i + k, "Amount"] = account.iloc[year, i]
            if drop is True:
                GL = GL[GL.Amount != 0].reset_index(drop=True)
            return GL

        list_of_accounts = [
            self.Liability_on_Initial_Recognition,
            self.Reconciliation_of_Best_Estimate_Liability,
            self.Expected_Cashflow,
            self.Actual_Cashflow,
            self.Expected_Risk_Adjustment_CF,
            self.Actual_Risk_Adjustment_CF,
            self.Reconciliation_of_Contractual_Service_Margin,
            self.Reconciliation_of_Total_Contract_Liability,
            self.Reconciliation_of_Risk_Adjustment,
            self.Reconciliation_of_Acquisition_Expense_Amortisation,
            self.Statement_of_Profit_or_Loss,
        ]
        list_of_account_abv = [
            "LIR",
            "BEL",
            "ECF",
            "ACF",
            "ERA",
            "ARA",
            "CSM",
            "TCL",
            "RRA",
            "AEA",
            "PL",
        ]

        for accounts, name in zip(list_of_accounts, list_of_account_abv):
            if name == "LIR":
                if year == 0:
                    GL = add_account(GL, accounts, name, drop_zeros)
            else:
                GL = add_account(GL, accounts, name, drop_zeros)

        return round(GL).to_csv(str("Chart of Accounts - GMM_" + str(year) + ".csv"))


assumptions = pd.read_csv("data/Assumptions.csv")
ifrs = GMM(assumptions)

for i in range(len(assumptions)):
    ifrs.Chart_of_Accounts(i, True)
ifrs.All_Statements()
