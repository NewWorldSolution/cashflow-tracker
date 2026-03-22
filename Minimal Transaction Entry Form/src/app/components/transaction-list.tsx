import { useNavigate } from "react-router";

interface Transaction {
  id: string;
  date: string;
  category: string;
  direction: "income" | "expense";
  amount: number;
  paymentMethod: string;
  loggedBy: string;
}

export function TransactionList() {
  const navigate = useNavigate();

  // Mock data - in a real app this would come from a database
  const transactions: Transaction[] = [
    {
      id: "1",
      date: "2026-03-22",
      category: "Office supplies",
      direction: "expense",
      amount: 245.50,
      paymentMethod: "Card",
      loggedBy: "Anna"
    },
    {
      id: "2",
      date: "2026-03-21",
      category: "Software & subscriptions",
      direction: "expense",
      amount: 99.00,
      paymentMethod: "Transfer",
      loggedBy: "Mark"
    },
    {
      id: "3",
      date: "2026-03-20",
      category: "Professional services",
      direction: "income",
      amount: 1500.00,
      paymentMethod: "Transfer",
      loggedBy: "Sarah"
    },
    {
      id: "4",
      date: "2026-03-19",
      category: "Marketing & advertising",
      direction: "expense",
      amount: 420.00,
      paymentMethod: "Card",
      loggedBy: "Anna"
    },
    {
      id: "5",
      date: "2026-03-18",
      category: "Travel & accommodation",
      direction: "expense",
      amount: 185.00,
      paymentMethod: "Cash",
      loggedBy: "Mark"
    },
    {
      id: "6",
      date: "2026-03-17",
      category: "Equipment",
      direction: "expense",
      amount: 750.00,
      paymentMethod: "Transfer",
      loggedBy: "Sarah"
    },
    {
      id: "7",
      date: "2026-03-16",
      category: "Professional services",
      direction: "income",
      amount: 2200.00,
      paymentMethod: "Transfer",
      loggedBy: "Anna"
    },
    {
      id: "8",
      date: "2026-03-15",
      category: "Office supplies",
      direction: "expense",
      amount: 67.30,
      paymentMethod: "Card",
      loggedBy: "Mark"
    },
    {
      id: "9",
      date: "2026-03-14",
      category: "Utilities",
      direction: "expense",
      amount: 320.00,
      paymentMethod: "Transfer",
      loggedBy: "Sarah"
    },
    {
      id: "10",
      date: "2026-03-13",
      category: "Software & subscriptions",
      direction: "expense",
      amount: 49.00,
      paymentMethod: "Card",
      loggedBy: "Anna"
    },
    {
      id: "11",
      date: "2026-03-12",
      category: "Professional services",
      direction: "income",
      amount: 1800.00,
      paymentMethod: "Transfer",
      loggedBy: "Mark"
    },
    {
      id: "12",
      date: "2026-03-11",
      category: "Marketing & advertising",
      direction: "expense",
      amount: 890.00,
      paymentMethod: "Transfer",
      loggedBy: "Sarah"
    },
    {
      id: "13",
      date: "2026-03-10",
      category: "Office supplies",
      direction: "expense",
      amount: 125.80,
      paymentMethod: "Cash",
      loggedBy: "Anna"
    },
    {
      id: "14",
      date: "2026-03-09",
      category: "Travel & accommodation",
      direction: "expense",
      amount: 450.00,
      paymentMethod: "Card",
      loggedBy: "Mark"
    },
    {
      id: "15",
      date: "2026-03-08",
      category: "Professional services",
      direction: "income",
      amount: 3100.00,
      paymentMethod: "Transfer",
      loggedBy: "Sarah"
    },
    {
      id: "16",
      date: "2026-03-07",
      category: "Equipment",
      direction: "expense",
      amount: 299.00,
      paymentMethod: "Card",
      loggedBy: "Anna"
    },
    {
      id: "17",
      date: "2026-03-06",
      category: "Software & subscriptions",
      direction: "expense",
      amount: 199.00,
      paymentMethod: "Transfer",
      loggedBy: "Mark"
    },
    {
      id: "18",
      date: "2026-03-05",
      category: "Office supplies",
      direction: "expense",
      amount: 78.50,
      paymentMethod: "Cash",
      loggedBy: "Sarah"
    },
    {
      id: "19",
      date: "2026-03-04",
      category: "Marketing & advertising",
      direction: "expense",
      amount: 560.00,
      paymentMethod: "Card",
      loggedBy: "Anna"
    },
    {
      id: "20",
      date: "2026-03-03",
      category: "Professional services",
      direction: "income",
      amount: 2500.00,
      paymentMethod: "Transfer",
      loggedBy: "Mark"
    }
  ];

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", { 
      year: "numeric", 
      month: "short", 
      day: "numeric" 
    });
  };

  const formatAmount = (amount: number, direction: "income" | "expense") => {
    const formatted = amount.toFixed(2);
    return direction === "income" ? `+${formatted}` : `−${formatted}`;
  };

  const getRowColor = (direction: "income" | "expense") => {
    return direction === "income" ? "text-blue-700" : "text-gray-900";
  };

  return (
    <div className="min-h-screen bg-white py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-2xl font-normal text-gray-900">Transactions</h1>
          <button
            onClick={() => navigate("/new")}
            className="px-6 py-2 bg-gray-900 text-white hover:bg-gray-800 transition-colors"
          >
            New Transaction
          </button>
        </div>

        {/* Transaction Table */}
        <div className="border border-gray-300">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-300 bg-gray-50">
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                  Date
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                  Category
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                  Direction
                </th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-700">
                  Amount
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                  Payment
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-700">
                  Logged by
                </th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((transaction) => (
                <tr 
                  key={transaction.id} 
                  className={`border-b border-gray-200 hover:bg-gray-50 transition-colors ${getRowColor(transaction.direction)}`}
                >
                  <td className="px-4 py-4 text-sm">
                    {formatDate(transaction.date)}
                  </td>
                  <td className="px-4 py-4 text-sm">
                    {transaction.category}
                  </td>
                  <td className="px-4 py-4 text-sm">
                    <span className="capitalize">
                      {transaction.direction}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm text-right font-medium">
                    {formatAmount(transaction.amount, transaction.direction)}
                  </td>
                  <td className="px-4 py-4 text-sm">
                    {transaction.paymentMethod}
                  </td>
                  <td className="px-4 py-4 text-sm">
                    {transaction.loggedBy}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Footer note */}
        <p className="mt-4 text-xs text-gray-500">
          Showing last 20 transactions
        </p>
      </div>
    </div>
  );
}