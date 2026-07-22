import { useState } from "react";
import { ApiError, api } from "../api/client";
import { useApi } from "../api/useApi";
import type { User } from "../api/types";
import { useAuth } from "../auth/useAuth";
import { PageHeader } from "../components/PageHeader";
import { ErrorState, Loading } from "../components/States";
import { formatDate } from "../lib/format";
import styles from "./ProfilePage.module.css";

export function ProfilePage() {
  const { user, refresh } = useAuth();

  return (
    <>
      <PageHeader title="Profile" subtitle="Your account and, for admins, team management." />
      {user && <ProfileForm user={user} onSaved={refresh} />}
      {user?.role === "admin" && <UserList currentUserId={user.id} />}
    </>
  );
}

function ProfileForm({ user, onSaved }: { user: User; onSaved: () => Promise<void> }) {
  const [fullName, setFullName] = useState(user.full_name);
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setNotice(null);
    setError(null);
    setSaving(true);
    try {
      const body: Record<string, string> = {};
      if (fullName !== user.full_name) body.full_name = fullName;
      if (password) body.password = password;
      if (Object.keys(body).length > 0) {
        await api.patchJson<User>("/users/me", body);
        await onSaved();
      }
      setPassword("");
      setNotice("Profile updated");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Update failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className={`card ${styles.card}`}>
      <div className={styles.identity}>
        <div>
          <div className={styles.email}>{user.email}</div>
          <div className="muted">
            <span className="tag">{user.role}</span> · joined {formatDate(user.created_at)}
          </div>
        </div>
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div>
          <label className="field-label" htmlFor="fullName">
            Full name
          </label>
          <input
            id="fullName"
            className="input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
        </div>
        <div>
          <label className="field-label" htmlFor="newPassword">
            New password <span className="muted">(leave blank to keep current)</span>
          </label>
          <input
            id="newPassword"
            className="input"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {notice && <p className={styles.ok}>{notice}</p>}
        {error && <p className={styles.err}>{error}</p>}

        <div>
          <button className="btn btn-primary" type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save changes"}
          </button>
        </div>
      </form>
    </div>
  );
}

function UserList({ currentUserId }: { currentUserId: string }) {
  const { data, loading, error, reload } = useApi(() => api.get<User[]>("/users"));

  async function handleDelete(user: User) {
    if (!confirm(`Delete ${user.email}?`)) return;
    try {
      await api.del(`/users/${user.id}`);
      reload();
    } catch {
      alert("Could not delete user");
    }
  }

  return (
    <section className={styles.section}>
      <h2 className={styles.heading}>Team members</h2>
      {loading && <Loading />}
      {error && <ErrorState message={error} onRetry={reload} />}
      {data && (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {data.map((member) => (
                <tr key={member.id}>
                  <td className={styles.memberName}>{member.full_name}</td>
                  <td className="muted">{member.email}</td>
                  <td>
                    <span className="tag">{member.role}</span>
                  </td>
                  <td className="muted">{formatDate(member.created_at)}</td>
                  <td className={styles.right}>
                    {member.id !== currentUserId && (
                      <button
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDelete(member)}
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
