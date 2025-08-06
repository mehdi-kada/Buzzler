import "./globals.css";
import { AuthInitializer } from "@/components/auth/initializer/AuthInitializer";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthInitializer />
        {children}
      </body>
    </html>
  );
}
