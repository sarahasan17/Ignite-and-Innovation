@Test
void testDeactivateProxy_Success() {
    // Mock user returned from UserDetails (or LDAPService, depending on your design)
    LDAPUserInfoDto currentUser = new LDAPUserInfoDto();
    currentUser.setEmplId("currentEmp123");
    currentUser.setAdEntId("adCurrent");

    // Simulate getting user details
    when(ldapService.getUserByEmpld("proxyEmp123")).thenReturn(currentUser);

    // Mock CriteriaBuilder and other JPA criteria API components
    CriteriaBuilder cb = mock(CriteriaBuilder.class);
    CriteriaQuery<UsrProxy> cq = mock(CriteriaQuery.class);
    Root<UsrProxy> root = mock(Root.class);

    when(entityManager.getCriteriaBuilder()).thenReturn(cb);
    when(cb.createQuery(UsrProxy.class)).thenReturn(cq);
    when(cq.from(UsrProxy.class)).thenReturn(root);

    // Mock TypedQuery result
    javax.persistence.TypedQuery<UsrProxy> typedQuery = mock(javax.persistence.TypedQuery.class);
    when(entityManager.createQuery(any(CriteriaQuery.class))).thenReturn(typedQuery);

    UsrProxy usrProxy = new UsrProxy();
    usrProxy.setEmpld("adCurrent");
    usrProxy.setProxyEmpld("proxyEmp123");
    usrProxy.setActiveDate(ZonedDateTime.now());
    usrProxy.setInactiveDate(null); // initially active

    when(typedQuery.getResultList()).thenReturn(Collections.singletonList(usrProxy));

    // Execute
    ProxyAssignmentResult result = proxyAssignmentService.deactivateProxy("proxyEmp123", 1L, "currentEmp123");

    // Verify
    assertNotNull(result);
    assertEquals("OK", result.getMessage());
    assertEquals("OK", result.getResult());
    assertNotNull(usrProxy.getInactiveDate()); // should be set now
    verify(usrProxyDao).save(usrProxy);
}
