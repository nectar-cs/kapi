copy_tree = {
  "does_svc_connect": {
    "summary": lambda args:
    f"Let's make sure there's a problem first. Let's connect to "
    f"{args['dep_name']} from its service {args['svc_name']} "
    f"via port {args['port']}."
    ,
    "steps": lambda args: [
      f"Create/reuse a stunt pod to send a cURL from",
      f"Tell the stunt pod to cURL {args['svc_name']} on port {args['port']}"
    ],
    "commands": lambda args: [
      f"kubectl exec {args['pod_name']} -- curl {args['target_url']}"
    ],
    "conclusion": {
      "positive": lambda args: [f"The Service -> Pod -> Container -> App chain is working."],
      "negative": lambda args: [f"Could not connect, there is indeed a problem."]
    },
  },

  "is_svc_visible": {
    "summary": lambda args:
    f"We're going to check if the cluster's DNS can resolve {args['svc_name']}'s "
    f"partially qualified domain name - {args['fqdn']}."
    ,
    "steps": lambda args: [
      f"Run nslookup against {args['svc_name']} from inside the cluster",
      f"Check that there is an entry for {args['fqdn']}"
    ],
    "commands": lambda args: [
      f"kubectl run {args['pod_name']} --image=nectar_cs/curler:latest "
      f"-n {args['ns']}",
      f"kubectl exec {args['pod_name']} nslookup {args['fqdn']}"
    ],
    "conclusion": {
      "positive": lambda args: [
        f"The cluster's DNS is working, huge relief.",
        f"This means {args['fqdn']} -> {args['svc_ip']} is happening correctly."
      ],
      "negative": lambda args: [
        f"This is the Problem. Continue for remediation."
      ]
    },
  },

  "does_svc_see_pods": {
    "summary": lambda args: (
      f"We're going to check whether the service {args['svc_name']} 'sees' "
      f"any pods at all, where it's meant to forward traffic to."
    ),
    "steps": lambda args: [
      f"Get {args['svc_name']}'s 'endpoints' (target pod IPs)",
      f"Check if that list is empty or not"
    ],
    "commands": lambda args: [
      f"kubectl get endpoints {args['svc_name']} -n {args['ns']} "
    ],
    "conclusion": {
      "positive": lambda args: [
        f"{args['svc_name']} knows to forward traffic to {args['ep_count']} pods.",
        f"Next, we're going to check if those are the right pods"
      ],
      "negative": lambda args: [
        f"Things are failing because {args['svc_name']} isn't forwarding traffic anywhere.",
        f"Let's find out why."
      ]
    },
  },

  "does_svc_see_right_pods": {
    "summary": lambda args: (
      f"Is the service pointing to the deployment {args['svc_name']}'s "
      f"pods or some other random pods?"
    ),
    "steps": lambda args: [
      f"Get {args['svc_name']}'s 'endpoints', i.e target podIPs",
      f"Get the IPs of all of {args['dep_name']}'s pods"
      f"Check that 100% of the returned IPs belong to the found pods"
    ],
    "commands": lambda args: [
      f"kubectl get endpoints {args['svc_name']} -n {args['ns']}",
      f"kubectl get pods -l {args['pod_label_comp']} -n {args['ns']}"
    ],
    "conclusion": {
      "positive": lambda args: [
        f"Big win. Now we can look at the pod level."
      ],
      "negative": lambda args: [
        f"{args['svc_name']} is pointing to one or more pods that don't belong"
        f" to its deployment ({args['dep_name']})."
      ]
    },
  },

  "does_dns_work": {
    "summary": lambda args: (
      f"We have to check if machinery that does domain name resolution (DNS). "
      f"In the case of a Kubernetes cluster, that's the CoreDNS or "
      f"KubeDNS pods running in kube-system."
    ),
    "steps": lambda args: [
      f"List pods in the kube-system namespace",
      f"Filter by label match k8s-app=kube-dns",
      f"Check that at least one is running"
    ],
    "commands": lambda args: [
      f"kubectl get pods -n kube-system -l k8s-app=kube-dns"
    ],
    "conclusion": {
      "positive": lambda args: [
        f"The cluster's DNS is working. Thank god."
      ],
      "negative": lambda args: [
        f"This is a cluster level problem, unrelated to {args['dep_name']}.",
        f"This is the Problem. Continue for remediation."
      ]
    }
  },

  "do_pods_connect": {
    "summary": lambda args: (
      f"Check if 100% of {args['dep_name']}'s pods are accepting HTTP requests. "
      f"We'll ignore the service ({args['svc_name']}) here and go straight for the pods' IPs"
    ),
    "steps": lambda args: [
      f"Get list of {args['dep_name']}'s pods.",
      f"cURL each one directly by using their IP instead of the service's."
    ],
    "commands": lambda args: [
      f"pods=$(kubectl get pods -l {args['pod_label_comp']} -n {args['ns']})",
      f"for $pod in $pods:"
      f"    $ip=echo $pod | jq .status.pod_ip",
      f"    $name=echo $pod | jq .metadata.name",
      f"    kubectl exec $name -- curl $ip"
    ],
    "conclusion": {
      "positive": lambda args: [f"All pods connected."],
      "negative": lambda args: [
        f"{args['culprits']} could not connect."
      ]
    },
  },

  "are_pods_running": {
    "summary": lambda args: (
      f"Make sure at least one of {args['dep_name']}'s pods running?"
    ),
    "steps": lambda args: [
      f"Get list of {args['dep_name']}'s pods",
      f"Count how many have status Running",
      f"Make sure no pods have non-starting containers"
    ],
    "commands": lambda args: [
      f"pods=$(kubectl get pods -l {args['pod_label_comp']} -n {args['ns']} -o json)",
      "echo $pods | jq .items[].status.phase",
      "echo $pods | jq .items[].status.containerStatuses[].state"
    ],
    "conclusion": {
      "positive": lambda args: [
        f"{args['pods_running']}/{args['pods_total']} pods running"
      ],
      "negative": lambda args: [
        f"{args['pods_not_running']}/{args['pods_total']} pods not running",
        f"This is the Problem. Continue for remediation."
      ]
    },
  }
}