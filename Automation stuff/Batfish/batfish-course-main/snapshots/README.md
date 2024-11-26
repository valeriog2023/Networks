|Snapshot Name | Changes |
|--------|---------|
| 001_base   | Base snapshot. No issues introduced |
| 002_config | No issues introduced |
| 003_control_plane | nxos-core1[Ethernet1/2] and nxos-aggr2[Ethernet1/5] DEAD INTERNAL set to incorrect value of 30
|| ACL with deny any any on aggr1 link |
|| aggr2 remote-as 64529 added for core2 peering
| 004_routing | Updated Ethernet1/1 on core to shutdown |
| 005_l3_forwarding | Added ACL deny 8080 on aggr1 to server2 |
| 006_l2_forwarding | ios1 pruned to VLAN99 on Port-channel20 |
| 007_acls |  core1/2 have ACLs applied inbound from aggrs |
|  |  core1 has ACL shadowing applied |
|  |  core1 is allowing the wrong subnet |
| 008a_diff_comparision | No issues introduced |
| 008b_diff_comparision | core1 has a ACL deny all, blocking BGP peering |
| 009a_acl_compare | ACLs for DNS and HTTPS for server blocks |
| 009b_acl_compare | ACLs/groups remove a DNS IP and add a new server block. |
| 010a_diff_reachability | No issues introduced |
| 010b_diff_reachability | Deny tcp/888 on core1 links to aggrs |
| 011_snapshot_forking | No issues introduced |
| 012_impact_analysis | No issues introduced |
| 013_assertions | No issues introduced |
| 014_pytest | Duplicate router ids |
