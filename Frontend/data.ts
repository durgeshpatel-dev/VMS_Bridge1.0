import { Severity, Vulnerability } from './types';

export const VulnList: Vulnerability[] = [
  { 
    id: '1', 
    severity: Severity.CRITICAL, 
    name: 'Log4j RCE Vulnerability', 
    cve: 'CVE-2021-44228', 
    asset: 'production-api-server-01', 
    discoveredAt: '2 hours ago',
    aiScore: 98,
    status: 'Open',
    description: 'Apache Log4j2 2.0-beta9 through 2.12.1 and 2.13.0 through 2.15.0 JNDI features used in configuration, log messages, and parameters do not protect against attacker controlled LDAP and other JNDI related endpoints.',
    remediation: 'Upgrade Log4j to version 2.17.0 or later immediately. Use the following command to update dependency:\nmvn versions:use-latest-releases -Dincludes=org.apache.logging.log4j:log4j-core',
    jiraKey: 'KAN-4921'
  },
  { 
    id: '2', 
    severity: Severity.HIGH, 
    name: 'Weak SSL Cipher Suite', 
    cve: 'SSL-002', 
    asset: 'load-balancer-public', 
    discoveredAt: '5 hours ago',
    aiScore: 72,
    status: 'Open',
    description: 'The remote service supports the use of weak SSL ciphers. This configuration allows attackers to decrypt traffic or perform man-in-the-middle attacks.',
    remediation: 'Reconfigure the affected SSL/TLS service to disable weak ciphers. Ensure only TLS 1.2 or 1.3 is enabled with strong cipher suites.'
  },
  { 
    id: '3', 
    severity: Severity.MEDIUM, 
    name: 'Outdated NGINX Version', 
    cve: 'PKO-058', 
    asset: 'internal-dashboard-v2', 
    discoveredAt: '1 day ago',
    aiScore: 45,
    status: 'In Progress',
    description: 'The version of NGINX running on the remote host is affected by multiple vulnerabilities. Updating to the latest stable version is recommended.',
    remediation: 'Update NGINX to the latest stable version provided by your package manager.'
  },
  { 
    id: '4', 
    severity: Severity.MEDIUM, 
    name: 'Missing X-Frame-Options', 
    cve: 'HTTP-012', 
    asset: 'customer-portal-web', 
    discoveredAt: '2 days ago',
    aiScore: 30,
    status: 'Open',
    description: 'The remote web server does not set an X-Frame-Options response header. This may expose the site to Clickjacking attacks.',
    remediation: 'Configure the web server to include the X-Frame-Options header with a value of DENY or SAMEORIGIN.'
  },
  { 
    id: '5', 
    severity: Severity.LOW, 
    name: 'Exposed Git Config', 
    cve: 'GIT-001', 
    asset: 'dev-testing-env', 
    discoveredAt: '3 days ago',
    aiScore: 20,
    status: 'Fixed',
    description: 'The .git/config file is accessible on the web server. This file contains information about the repository configuration and may expose internal details.',
    remediation: 'Configure the web server to deny access to the .git directory and its contents.'
  },
];