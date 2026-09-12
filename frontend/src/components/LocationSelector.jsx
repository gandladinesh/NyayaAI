import { useState, useEffect } from "react";

export default function LocationSelector({
  selectedState,
  selectedDistrict,
  onStateChange,
  onDistrictChange,
  disabled = false,
  apiBaseUrl = "http://127.0.0.1:8000/api",
}) {
  const [states, setStates] = useState([]);
  const [districts, setDistricts] = useState([]);
  const [loadingStates, setLoadingStates] = useState(false);
  const [loadingDistricts, setLoadingDistricts] = useState(false);
  const [locationError, setLocationError] = useState("");

  // Load states on initial mount
  useEffect(() => {
    let isMounted = true;
    const fetchStates = async () => {
      setLoadingStates(true);
      setLocationError("");
      try {
        const response = await fetch(`${apiBaseUrl}/states`);
        if (!response.ok) {
          throw new Error(`Failed to load states: ${response.status}`);
        }
        const data = await response.json();
        if (isMounted) {
          setStates(data);
        }
      } catch (err) {
        console.error("LocationSelector fetchStates error:", err);
        if (isMounted) {
          setLocationError("Unable to load states. Please ensure the backend server is running.");
        }
      } finally {
        if (isMounted) {
          setLoadingStates(false);
        }
      }
    };

    fetchStates();
    return () => {
      isMounted = false;
    };
  }, [apiBaseUrl]);

  // Load districts when selectedState changes
  useEffect(() => {
    let isMounted = true;
    if (!selectedState) {
      setDistricts([]);
      return;
    }

    const fetchDistricts = async () => {
      setLoadingDistricts(true);
      setLocationError("");
      try {
        const response = await fetch(`${apiBaseUrl}/states/${selectedState}/districts`);
        if (!response.ok) {
          throw new Error(`Failed to load districts: ${response.status}`);
        }
        const data = await response.json();
        if (isMounted) {
          setDistricts(data);
        }
      } catch (err) {
        console.error("LocationSelector fetchDistricts error:", err);
        if (isMounted) {
          setLocationError("Unable to load districts for selected state.");
        }
      } finally {
        if (isMounted) {
          setLoadingDistricts(false);
        }
      }
    };

    fetchDistricts();
    return () => {
      isMounted = false;
    };
  }, [selectedState, apiBaseUrl]);

  const handleStateSelect = (e) => {
    const newStateId = e.target.value;
    const stObj = states.find((s) => s.state_id === newStateId);
    onStateChange(newStateId, stObj);
    // Reset district selection when state changes
    onDistrictChange("", null);
  };

  const handleDistrictSelect = (e) => {
    const newDistrictId = e.target.value;
    const dtObj = districts.find((d) => d.district_id === newDistrictId);
    onDistrictChange(newDistrictId, dtObj);
  };

  return (
    <div className="location-selector-group">
      <div className="input-field">
        <label htmlFor="state-select" className="input-label">
          State / Union Territory <span className="required-star">*</span>
        </label>
        <select
          id="state-select"
          className="select-input"
          value={selectedState}
          onChange={handleStateSelect}
          disabled={disabled || loadingStates}
        >
          <option value="">
            {loadingStates ? "Loading states..." : "-- Select State / UT --"}
          </option>
          {states.map((st) => (
            <option key={st.state_id} value={st.state_id}>
              {st.state_name} {st.is_union_territory ? "(UT)" : ""}
            </option>
          ))}
        </select>
      </div>

      <div className="input-field">
        <label htmlFor="district-select" className="input-label">
          District <span className="required-star">*</span>
        </label>
        <select
          id="district-select"
          className="select-input"
          value={selectedDistrict}
          onChange={handleDistrictSelect}
          disabled={disabled || !selectedState || loadingDistricts}
        >
          <option value="">
            {!selectedState
              ? "-- Select a state first --"
              : loadingDistricts
              ? "Loading districts..."
              : "-- Select District --"}
          </option>
          {districts.map((dst) => (
            <option key={dst.district_id} value={dst.district_id}>
              {dst.district_name}
            </option>
          ))}
        </select>
      </div>

      {locationError && (
        <div className="location-error-banner" role="alert">
          <span>⚠️ {locationError}</span>
        </div>
      )}
    </div>
  );
}
