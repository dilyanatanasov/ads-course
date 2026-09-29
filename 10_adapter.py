"""SESSION 10 - Adapter.

    python 10_adapter.py

THE SITUATION
    The university's payment provider has an API written in 2007. It takes XML
    in a string, returns status codes in a string, and counts money in
    stotinki where you count leva. You do not own it and you may not change
    one character of it.

    Read LegacyBankGateway as a victim, not a critic. Half of all professional
    work is this: keeping a mess contained when the mess is not yours.

THE IDEA
    One class speaks 2007 on one side and offers charge(account, leva) on the
    other. All the ugliness lives in that class, and the rest of the system
    never learns the bank exists.

FIRST RUN LOOKS BROKEN. IT IS NOT.
    You get a traceback instead of PASS/FAIL, because the methods below raise
    NotImplementedError until you write them. The last line of the traceback
    names the method to start with.

YOUR TASK (25 min)
    1. BankAdapter.charge(account, leva)
         - leva to stotinki. 120.50 leva is 12050 stotinki, and
           int(leva * 100) is WRONG - floats make that 12049.999999999998.
           Use round(). This is a real bug that costs real money.
         - build the XML, call do_payment, read the response.
         - on error raise PaymentFailed, KEEPING the bank's own code.
    2. FakePaymentGateway - same interface, no bank. Four lines.
    3. Write the four remaining checks at the bottom.

    The error code must survive. An adapter that translates the interface and
    throws away the diagnostics has not helped you - it has blindfolded you at
    3am. Translate the shape, preserve the evidence.

THE COST
    Adapters hide things, including the parts you needed to see. Your clean
    interface says PaymentFailed; the useful detail was discarded by your own
    code unless you deliberately kept it.
"""
import re
from abc import ABC, abstractmethod
from check import check


class LegacyBankGateway:
    """The bank's API. Do not edit."""

    def __init__(self):
        self.ledger = []

    def do_payment(self, xml_request):
        acct = re.search(r"<acct>(.*?)</acct>", xml_request)
        amount = re.search(r"<amt>(.*?)</amt>", xml_request)
        if not acct or not amount:
            return "STATUS=ERR;CODE=E_MALFORMED_0001"
        stotinki = int(amount.group(1))
        if stotinki <= 0:
            return "STATUS=ERR;CODE=E_AMOUNT_0007"
        if stotinki > 100000:
            return "STATUS=ERR;CODE=E_INSUF_0042"
        self.ledger.append((acct.group(1), stotinki))
        return "STATUS=OK;REF=TX%05d" % len(self.ledger)


class PaymentFailed(Exception):
    def __init__(self, message, code=None):
        super().__init__(message)
        self.code = code


class PaymentPort(ABC):
    @abstractmethod
    def charge(self, account, leva):
        """Returns a transaction reference, or raises PaymentFailed."""


class BankAdapter(PaymentPort):
    def __init__(self, bank):
        self.bank = bank

    def charge(self, account, leva):
        # TODO: leva -> stotinki, build the XML, call do_payment,
        # parse "STATUS=OK;REF=..." and return the ref, or raise
        # PaymentFailed(code=...) keeping the bank's error code.
        raise NotImplementedError


class FakePaymentGateway(PaymentPort):
    def __init__(self):
        self.charged = []

    def charge(self, account, leva):
        raise NotImplementedError    # TODO: record and return "FAKE-1", ...


if __name__ == "__main__":
    print("SESSION 10 - adapter")
    bank = LegacyBankGateway()
    payments = BankAdapter(bank)

    # ---- STEP 2: the nice call we wished the bank gave us ----------------
    ref = payments.charge("BG80BNBG", 120.50)
    check("returns a reference", ref.startswith("TX"), True)

    # YOUR TURN - write one check for each, then make them pass:
    #   converted to stotinki   bank.ledger[0][1] after 120.50 leva. Work
    #                           the number out yourself, then try
    #                           int(120.50 * 100) before you trust it.
    #   failure raises          5000.00 leva is over the bank's limit
    #   keeps the error code    ...and exc.code is still "E_INSUF_0042".
    #                           Two checks, because "it failed" and "we can
    #                           still tell why" are different promises, and
    #                           adapters usually break the second one.
    #   fake gateway            FakePaymentGateway().charge("acct", 10.0)
    #   fake recorded it        ...and .charged holds ("acct", 10.0)
