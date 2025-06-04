document.addEventListener('DOMContentLoaded', () => {
    const viewButtons = document.querySelectorAll('.view-applications');
    viewButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const jobId = button.dataset.jobId;
            const applicationsList = document.getElementById(`applications-${jobId}`);
            
            try {
                const response = await fetch(`/job/${jobId}/applications`);
                const applications = await response.json();
                
                applicationsList.innerHTML = applications.length > 0
                    ? applications.map(app => `
                        <div class="application-item">
                            <p><strong>Name:</strong> ${app.candidate_name}</p>
                            <p><strong>Email:</strong> ${app.candidate_email}</p>
                            <p><strong>Resume:</strong> ${app.resume.substring(0, 100)}...</p>
                            <p><strong>Status:</strong> ${app.status}</p>
                            <select onchange="updateStatus(${app.id}, this.value)">
                                <option value="pending" ${app.status === 'pending' ? 'selected' : ''}>Pending</option>
                                <option value="accepted" ${app.status === 'accepted' ? 'selected' : ''}>Accepted</option>
                                <option value="rejected" ${app.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                            </select>
                        </div>
                    `).join('')
                    : '<p>No applications yet.</p>';
            } catch (error) {
                console.error('Error fetching applications:', error);
                applicationsList.innerHTML = '<p>Error loading applications.</p>';
            }
        });
    });
});

async function updateStatus(appId, status) {
    try {
        const response = await fetch(`/application/${appId}/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `status=${status}`
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error('Error updating status:', error);
        alert('Error updating status.');
    }
}