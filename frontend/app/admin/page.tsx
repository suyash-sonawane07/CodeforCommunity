import { PageContainer } from "@/components/layouts";
import { Card, CardTitle, Field, Input, PageHeader, ScaffoldNotice } from "@/components/ui";

/**
 * TODO(Member A, PRD S-04): Admin login form (demo auth via POST /auth/login;
 * production auth is explicitly out of scaffold scope).
 */
export default function AdminLoginPage() {
  return (
    <PageContainer>
      <PageHeader
        title="Staff login"
        subtitle="Analyst, reviewer, decision-maker and admin roles."
      />
      <Card className="max-w-sm">
        <CardTitle>Sign in</CardTitle>
        <div className="mt-3 space-y-3">
          <Field label="Email">
            <Input id="email" name="email" type="email" disabled placeholder="scaffold" />
          </Field>
          <Field label="Password">
            <Input id="password" name="password" type="password" disabled placeholder="scaffold" />
          </Field>
        </div>
      </Card>
      <ScaffoldNotice screen="S-04 Admin Login" />
    </PageContainer>
  );
}
