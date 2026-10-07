import jenkins.model.Jenkins
import org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob

def jenkins = Jenkins.get()
def jobName = 'delivery-monitoring'
def job = jenkins.getItem(jobName)

if (job == null) {
    job = jenkins.createProject(WorkflowJob, jobName)
}

def pipelineFile = new File('/opt/delivery-monitoring/Jenkinsfile')
job.setDefinition(new CpsFlowDefinition(pipelineFile.text, true))
job.save()
job.scheduleBuild2(0)