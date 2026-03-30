import { useEffect, useState } from "react";
import studentService from "../../api/studentService";
import Loader from "../../components/common/Loader";
import "../../styles/dashboard.css";

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await studentService.getProfile();
      const data = res.data?.data || res.data;
      setProfile(data);
      setFormData(data);
      setError(null);
    } catch (err) {
      console.error(err.response?.data || err.message);
      setError("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccess(null);

    try {
      // Only send editable fields
      let payload = {};

      if (profile.role === "STUDENT") {
        payload = {
          department: formData.department,
          year: Number(formData.year),
        };
      } else {
        payload = {
          department: formData.department,
          designation: formData.designation,
        };
      }

      await studentService.updateProfile(payload);
      await fetchProfile();
      setIsEditing(false);
      setSuccess("Profile updated successfully");
    } catch (err) {
      console.error(err.response?.data || err.message);
      setError("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loader />;
  if (error) return <div className="page-wrapper">{error}</div>;

  return (
    <div className="page-wrapper">
      <h1>{profile.role} Profile</h1>
      <p className="page-subtitle">Manage your personal details</p>

      <div className="card profile-form">

        {/* VIEW MODE */}
        {!isEditing && (
          <>
            <div className="form-group">
              <label>Name</label>
              <input value={profile.name || ""} disabled />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input value={profile.email || ""} disabled />
            </div>

            <div className="form-group">
              <label>Username</label>
              <input value={profile.username || ""} disabled />
            </div>

            {profile.role === "STUDENT" && (
              <>
                <div className="form-group">
                  <label>Roll Number</label>
                  <input value={profile.roll_number || ""} disabled />
                </div>

                <div className="form-group">
                  <label>Department</label>
                  <input value={profile.department || ""} disabled />
                </div>

                <div className="form-group">
                  <label>Year</label>
                  <input value={profile.year || ""} disabled />
                </div>
              </>
            )}

            {profile.role === "FACULTY" && (
              <>
                <div className="form-group">
                  <label>Department</label>
                  <input value={profile.department || ""} disabled />
                </div>

                <div className="form-group">
                  <label>Designation</label>
                  <input value={profile.designation || ""} disabled />
                </div>
              </>
            )}

            <button
              className="btn-primary"
              onClick={() => setIsEditing(true)}
            >
              Update Profile
            </button>
          </>
        )}

        {/* EDIT MODE */}
        {isEditing && (
          <form onSubmit={handleSubmit}>
            {profile.role === "STUDENT" && (
              <>
                <div className="form-group">
                  <label>Department</label>
                  <input
                    name="department"
                    value={formData.department || ""}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Year</label>
                  <input
                    name="year"
                    type="number"
                    value={formData.year || ""}
                    onChange={handleChange}
                  />
                </div>
              </>
            )}

            {profile.role === "FACULTY" && (
              <>
                <div className="form-group">
                  <label>Department</label>
                  <input
                    name="department"
                    value={formData.department || ""}
                    onChange={handleChange}
                  />
                </div>

                <div className="form-group">
                  <label>Designation</label>
                  <input
                    name="designation"
                    value={formData.designation || ""}
                    onChange={handleChange}
                  />
                </div>
              </>
            )}

            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Save Changes"}
            </button>

            <button
              type="button"
              className="btn-secondary"
              onClick={() => setIsEditing(false)}
            >
              Cancel
            </button>
          </form>
        )}

        {success && <p className="success">{success}</p>}
      </div>
    </div>
  );
}