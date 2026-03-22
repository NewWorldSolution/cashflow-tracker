import { createBrowserRouter } from "react-router";
import { TransactionList } from "./components/transaction-list";
import { TransactionForm } from "./components/transaction-form";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: TransactionList,
  },
  {
    path: "/new",
    Component: TransactionForm,
  },
]);
