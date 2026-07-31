export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background">
      <div className="space-y-2 text-center">
        <h2 className="text-2xl font-semibold text-foreground">404 — Not Found</h2>
        <p className="text-muted-foreground">The page you are looking for does not exist.</p>
      </div>
    </main>
  );
}
