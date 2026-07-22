import { PageHeader } from "../components/PageHeader";
import { EmptyState } from "../components/States";

export function DeploymentsPage() {
  return (
    <>
      <PageHeader
        title="Deployments"
        subtitle="Serve registered models behind a prediction endpoint."
      />
      <EmptyState title="Deployments arrive in Sprint 7">
        Promoting a model to production will build a serving image and expose it through
        Kubernetes. This page will list the live prediction endpoints.
      </EmptyState>
    </>
  );
}
