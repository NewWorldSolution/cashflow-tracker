import { useState } from "react";
import { useNavigate } from "react-router";

interface FormData {
  date: string;
  direction: "income" | "expense" | "";
  amount: string;
  category: string;
  paymentMethod: string;
  vatRate: string;
  vatDeductible: string;
  description: string;
}

interface FormErrors {
  [key: string]: string;
}

export function TransactionForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    date: new Date().toISOString().split("T")[0],
    direction: "",
    amount: "",
    category: "",
    paymentMethod: "",
    vatRate: "23",
    vatDeductible: "100",
    description: "",
  });
  
  const [errors, setErrors] = useState<FormErrors>({});
  const [showErrors, setShowErrors] = useState(false);

  const categories = [
    "Office supplies",
    "Software & subscriptions",
    "Travel & accommodation",
    "Marketing & advertising",
    "Professional services",
    "Equipment",
    "Utilities",
    "Other",
  ];

  const validateForm = (): FormErrors => {
    const newErrors: FormErrors = {};
    
    if (!formData.date) {
      newErrors.date = "Date is required";
    }
    
    if (!formData.direction) {
      newErrors.direction = "Please select income or expense";
    }
    
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      newErrors.amount = "Please enter a valid amount";
    }
    
    if (!formData.category) {
      newErrors.category = "Category is required";
    }
    
    if (!formData.paymentMethod) {
      newErrors.paymentMethod = "Payment method is required";
    }
    
    return newErrors;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors = validateForm();
    
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      setShowErrors(true);
      return;
    }
    
    // Mock submission - in real app would save to database
    console.log("Transaction submitted:", formData);
    
    // Reset form and navigate to list
    setFormData({
      date: new Date().toISOString().split("T")[0],
      direction: "",
      amount: "",
      category: "",
      paymentMethod: "",
      vatRate: "23",
      vatDeductible: "100",
      description: "",
    });
    setErrors({});
    setShowErrors(false);
    
    navigate("/");
  };

  const updateField = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const errorCount = Object.keys(errors).length;

  return (
    <div className="min-h-screen bg-white py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-normal text-gray-900">New Transaction</h1>
        </div>

        {/* Error Summary */}
        {showErrors && errorCount > 0 && (
          <div className="mb-6 p-4 border border-gray-300 bg-gray-50">
            <p className="text-sm text-gray-900 mb-2 font-medium">
              Please correct the following errors:
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              {Object.values(errors).map((error, idx) => (
                <li key={idx}>• {error}</li>
              ))}
            </ul>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Section: Basics */}
          <div className="mb-8 p-6 border border-gray-300">
            <h2 className="text-base font-medium text-gray-900 mb-4">Basics</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="date" className="block text-sm text-gray-700 mb-1">
                  Date
                </label>
                <input
                  type="date"
                  id="date"
                  value={formData.date}
                  onChange={(e) => updateField("date", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300"
                />
                {errors.date && (
                  <p className="mt-1 text-xs text-gray-600">{errors.date}</p>
                )}
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-2">
                  Direction
                </label>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => updateField("direction", "income")}
                    className={`flex-1 px-6 py-3 border ${
                      formData.direction === "income"
                        ? "border-gray-900 bg-gray-900 text-white"
                        : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                    } transition-colors`}
                  >
                    Income
                  </button>
                  <button
                    type="button"
                    onClick={() => updateField("direction", "expense")}
                    className={`flex-1 px-6 py-3 border ${
                      formData.direction === "expense"
                        ? "border-gray-900 bg-gray-900 text-white"
                        : "border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                    } transition-colors`}
                  >
                    Expense
                  </button>
                </div>
                {errors.direction && (
                  <p className="mt-1 text-xs text-gray-600">{errors.direction}</p>
                )}
              </div>
            </div>
          </div>

          {/* Section: Amount */}
          <div className="mb-8 p-6 border border-gray-300 bg-gray-50">
            <h2 className="text-base font-medium text-gray-900 mb-4">Amount</h2>
            
            <div>
              <label htmlFor="amount" className="block text-sm text-gray-700 mb-1">
                Enter gross amount (VAT included)
              </label>
              <input
                type="number"
                id="amount"
                step="0.01"
                placeholder="0.00"
                value={formData.amount}
                onChange={(e) => updateField("amount", e.target.value)}
                className="w-full px-4 py-3 text-lg border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300"
              />
              {errors.amount && (
                <p className="mt-1 text-xs text-gray-600">{errors.amount}</p>
              )}
            </div>
          </div>

          {/* Section: Details */}
          <div className="mb-8 p-6 border border-gray-300">
            <h2 className="text-base font-medium text-gray-900 mb-4">Details</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="category" className="block text-sm text-gray-700 mb-1">
                  Category
                </label>
                <select
                  id="category"
                  value={formData.category}
                  onChange={(e) => updateField("category", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300 bg-white"
                >
                  <option value="">Select category...</option>
                  {categories.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
                {errors.category && (
                  <p className="mt-1 text-xs text-gray-600">{errors.category}</p>
                )}
              </div>

              <div>
                <label htmlFor="paymentMethod" className="block text-sm text-gray-700 mb-1">
                  Payment method
                </label>
                <select
                  id="paymentMethod"
                  value={formData.paymentMethod}
                  onChange={(e) => updateField("paymentMethod", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300 bg-white"
                >
                  <option value="">Select method...</option>
                  <option value="cash">Cash</option>
                  <option value="card">Card</option>
                  <option value="transfer">Transfer</option>
                </select>
                {errors.paymentMethod && (
                  <p className="mt-1 text-xs text-gray-600">{errors.paymentMethod}</p>
                )}
              </div>
            </div>
          </div>

          {/* Section: VAT */}
          <div className="mb-8 p-6 border border-gray-300">
            <h2 className="text-base font-medium text-gray-900 mb-4">VAT</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="vatRate" className="block text-sm text-gray-700 mb-1">
                  VAT rate (%)
                </label>
                <select
                  id="vatRate"
                  value={formData.vatRate}
                  onChange={(e) => updateField("vatRate", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300 bg-white"
                >
                  <option value="0">0%</option>
                  <option value="5">5%</option>
                  <option value="8">8%</option>
                  <option value="23">23%</option>
                </select>
              </div>

              <div>
                <label htmlFor="vatDeductible" className="block text-sm text-gray-700 mb-1">
                  VAT deductible (%)
                </label>
                <select
                  id="vatDeductible"
                  value={formData.vatDeductible}
                  onChange={(e) => updateField("vatDeductible", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300 bg-white"
                >
                  <option value="0">0%</option>
                  <option value="50">50%</option>
                  <option value="100">100%</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section: Optional */}
          <div className="mb-8 p-6 border border-gray-300">
            <h2 className="text-base font-medium text-gray-900 mb-4">Optional</h2>
            
            <div>
              <label htmlFor="description" className="block text-sm text-gray-700 mb-1">
                Description
              </label>
              <textarea
                id="description"
                rows={3}
                value={formData.description}
                onChange={(e) => updateField("description", e.target.value)}
                placeholder="Add any additional notes..."
                className="w-full px-3 py-2 border border-gray-300 text-gray-900 focus:outline-none focus:border-blue-300 resize-none"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="submit"
              className="px-8 py-3 bg-gray-900 text-white hover:bg-gray-800 transition-colors"
            >
              Save Transaction
            </button>
            <button
              type="button"
              onClick={() => navigate("/")}
              className="px-6 py-3 border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
