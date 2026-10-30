import type { Metadata } from "next";
import "@xyflow/react/dist/style.css";
import "@/styles/tokens.css";
export const metadata: Metadata = {
  title: "Brian · DigiPlus Services",
  description:
    "Understand what changed, who it affects, and the evidence behind it.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
