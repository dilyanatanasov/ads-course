"""SESSION 10 - Adapter.

    python 10_adapter.py

THE SITUATION
    The university's payment provider has an API written in 2007. It speaks XML
    strings, returns status codes as strings, and uses stotinki where you use
    leva. You may NOT change it - you do not own it.

BUILD IT TOGETHER (15 min - we write this on the projector, you type along)
    STEP 1  Read LegacyBankGateway first, and read it as a VICTIM, not a
            critic. XML in a string, status codes in a string, money in
            stotinki. You may not change any of it.
            WHY THIS FRAMING MATTERS: half of all professional work is this.
            The skill is not writing clean code on an empty page, it is
            keeping a mess contained when you do not own the mess.

    STEP 2  Write the check before the adapter:
                ref = payments.charge("BG80BNBG", 120.50)
                check("returns a reference", ref.startswith("TX"), True)
            WHY WRITE THE NICE CALL FIRST: you have just specified the
            interface you WISH the bank had. Everything after this is
            translation. Design the inside-facing side first - the outside
            is not yours to design.

    STEP 3  Now the conversion, and go slowly here: 120.50 leva is 12050
            stotinki. `int(leva * 100)` is WRONG and will bite someone -
            floats make 120.50 * 100 come out as 12049.999999999998.
            Use round(). Say this out loud; it is a real production bug and
            it costs real money.

    STEP 4  Parse the response and raise PaymentFailed on ERR - but keep the
            code: PaymentFailed(message, code="E_INSUF_0042").
            WHY THE CODE SURVIVES: this is the rule the docstring's DOWNSIDE
            names. An adapter that translates the interface AND throws away
            the diagnostics has not helped you, it has blindfolded you at
            3am. Translate the shape; preserve the evidence.

    STEP 5  FakePaymentGateway - same interface, no bank, four lines.
            WHY IT IS ALLOWED TO BE THIS CHEAP: because PaymentPort defined
            what "a payment gateway" means. Once the interface is a real
            thing, a second implementation is almost free. That is the same
            move as session 04, applied to the outside world instead of a
            business rule.

YOUR JOB (25 min)
    Write BankAdapter so the rest of the system only ever sees charge(account,
    leva). All the 2007 lives in one class.
    Then write FakePaymentGateway - same interface, no bank - for testing.

THE TWIST
    The university switches provider next year. Your domain code does not
    change by one character.

THE DOWNSIDE
    Adapters hide things. When the bank starts failing, your clean interface
    says PaymentFailed and the useful detail - error code E_INSUF_0042 - was
    thrown away by your own adapter.
    RULE: translate the interface, preserve the diagnostics.
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

    # ---- NOW YOU WRITE THE REST ------------------------------------------
    #   "converted to stotinki"
    #       bank.ledger[0][1] after charging 120.50 leva. Work out the
    #       expected integer yourself, then try int(120.50 * 100) in a REPL
    #       before you trust it.
    #
    #   "failure raises" and "keeps the bank's error code"
    #       charging 5000.00 leva is over the bank's limit. Wrap it in
    #       try/except PaymentFailed and check BOTH that it raised and that
    #       exc.code is still the bank's own "E_INSUF_0042".
    #       WHY TWO CHECKS AND NOT ONE: "it failed" and "we can still tell
    #       WHY it failed" are two different promises, and the second one is
    #       the one adapters usually break.
    #
    #   "fake gateway" / "fake recorded it"
    #       FakePaymentGateway().charge("acct", 10.0) returns "FAKE-1" and
    #       records ("acct", 10.0). Decide the reference format yourselves -
    #       just make it obviously fake, so a fake reference can never be
    #       mistaken for a real one in a log.
    #
    # STRETCH: the bank returns E_MALFORMED_0001 for junk input. Write a
    #          check for what YOUR adapter does with it. Can it even happen,
    #          given your adapter builds the XML? Argue about it.
