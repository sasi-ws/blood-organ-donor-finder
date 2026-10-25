# One place for the blood compatibility rules (NFR-MNT-02).
# Key = patient's blood group. Value = donor groups that can give to that patient.
CAN_RECEIVE_FROM = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}


def compatible_donor_groups(patient_group):
    """Donor groups that can give to this patient group."""
    return CAN_RECEIVE_FROM.get(patient_group, [])


def match_label(patient_group, donor_group):
    """Label shown on each search result."""
    return "Exact match" if patient_group == donor_group else "Compatible"