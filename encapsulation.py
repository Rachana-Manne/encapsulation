"""Encapsulation practice: BankAccount and Bank classes."""

from numbers import Real


def _validate_amount(amount, action="Amount"):
    """Return amount if it is a positive real number, else raise ValueError."""
    if isinstance(amount, bool) or not isinstance(amount, Real):
        raise ValueError(f"{action} must be a number.")
    if amount <= 0:
        raise ValueError(f"{action} must be greater than zero.")
    return amount


class BankAccount:
    """A bank account that protects its internal state."""

    def __init__(self, account_number, holder_name, initial_balance=0):
        if not isinstance(account_number, str) or not account_number.strip():
            raise ValueError("Account number must be a non-empty string.")
        if isinstance(initial_balance, bool) or not isinstance(initial_balance, Real):
            raise ValueError("Initial balance must be a number.")
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        self.__account_number = account_number.strip()
        self.__holder_name = None
        self.__balance = initial_balance
        self.holder_name = holder_name  # reuse the validating setter

    # ---- account number: read-only ----
    @property
    def account_number(self):
        return self.__account_number

    # ---- holder name: getter + validated setter ----
    @property
    def holder_name(self):
        return self.__holder_name

    @holder_name.setter
    def holder_name(self, new_name):
        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("Holder name must be a non-empty string.")
        self.__holder_name = new_name.strip()

    # ---- balance: getter + validated setter ----
    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("Balance must be a number.")
        if value < 0:
            raise ValueError("Balance cannot be negative.")
        self.__balance = value

    # ---- operations ----
    def deposit(self, amount):
        _validate_amount(amount, "Deposit amount")
        self.__balance += amount

    def withdraw(self, amount):
        _validate_amount(amount, "Withdrawal amount")
        if amount > self.__balance:
            raise ValueError("Insufficient funds.")
        self.__balance -= amount

    def transfer(self, target_account, amount):
        """Move funds to another BankAccount; roll back if anything fails."""
        if not isinstance(target_account, BankAccount):
            raise TypeError("Target must be a BankAccount instance.")
        if target_account is self:
            raise ValueError("Cannot transfer to the same account.")

        self.withdraw(amount)  # raises ValueError if invalid / insufficient
        try:
            target_account.deposit(amount)
        except Exception as exc:
            self.__balance += amount  # rollback the withdrawal
            raise ValueError(f"Transfer failed and was rolled back: {exc}") from exc

    def __repr__(self):
        # Balance intentionally omitted.
        return f"BankAccount(account_number={self.__account_number!r}, holder={self.__holder_name!r})"


class Bank:
    """Holds accounts privately and exposes only safe operations."""

    def __init__(self):
        self.__accounts = []

    def add_account(self, account):
        if not isinstance(account, BankAccount):
            raise TypeError("Only BankAccount objects can be added.")
        if any(a.account_number == account.account_number for a in self.__accounts):
            raise ValueError(f"Account number {account.account_number} already exists.")
        self.__accounts.append(account)

    def get_account(self, account_number):
        for account in self.__accounts:
            if account.account_number == account_number:
                return account
        return None  # not found

    def list_accounts(self):
        """Return (account_number, holder_name) pairs only - balance stays hidden."""
        return [(a.account_number, a.holder_name) for a in self.__accounts]


if __name__ == "__main__":
    bank = Bank()
    alice = BankAccount("ACC001", "Alice Smith", 500)
    bob = BankAccount("ACC002", "Bob Jones")
    bank.add_account(alice)
    bank.add_account(bob)

    print("Accounts:", bank.list_accounts())

    alice.deposit(200)
    alice.withdraw(100)
    alice.transfer(bob, 250)
    print("Alice:", alice.balance, "| Bob:", bob.balance)

    # Error handling checks
    tests = {
        "negative initial balance": lambda: BankAccount("X", "Y", -5),
        "overdraw": lambda: bob.withdraw(10_000),
        "negative deposit": lambda: bob.deposit(-1),
        "negative balance set": lambda: setattr(bob, "balance", -10),
        "empty name": lambda: setattr(bob, "holder_name", "  "),
        "set account number": lambda: setattr(bob, "account_number", "HACK"),
        "duplicate account": lambda: bank.add_account(BankAccount("ACC001", "Eve")),
        "failed transfer": lambda: alice.transfer(bob, 10_000),
    }
    for label, action in tests.items():
        try:
            action()
            print(f"{label}: NO ERROR (unexpected)")
        except (ValueError, TypeError, AttributeError) as e:
            print(f"{label}: {type(e).__name__} -> {e}")

    # Name mangling: direct access fails, only the mangled name leaks through
    try:
        print(alice.__balance)
    except AttributeError as e:
        print("Direct access blocked:", e)