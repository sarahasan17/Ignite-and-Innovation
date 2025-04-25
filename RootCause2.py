@Test
void testGetAllADUsers_successful() throws ApplicationException {
    String searchFilter = "(memberOf=CN=TestGroup,OU=Users,DC=example,DC=com)";
    int pageSize = 2;

    LDAPUserInfoDto mockUser1 = new LDAPUserInfoDto();
    mockUser1.setEmpId("user1");

    List<LDAPUserInfoDto> mockUserList = List.of(mockUser1);

    // Setup mocks
    when(ldapTemplate.getContextSource()).thenReturn(contextSource);
    when(contextSource.getReadOnlyContext()).thenReturn(mock(LdapContext.class));

    // Mock the behavior of SingleContextSource (where doWithSingleContext() is invoked)
    try (MockedStatic<SingleContextSource> contextSourceMock = mockStatic(SingleContextSource.class)) {

        // Mock search result behavior
        LdapOperations ldapOperations = mock(LdapOperations.class);
        PagedResultsDirContextProcessor processor = mock(PagedResultsDirContextProcessor.class);

        // Simulate hasMore() returning true once, then false
        when(processor.hasMore()).thenReturn(true).thenReturn(false);

        // Simulate search call during the loop
        when(ldapOperations.search(
                eq(LdapUtils.emptyLdapName()),
                eq(searchFilter),
                any(SearchControls.class),
                any(PersonAttributesMapper.class),
                eq(processor)
        )).thenReturn(mockUserList);

        // Mock doWithSingleContext to invoke the real method
        contextSourceMock.when(() -> SingleContextSource.doWithSingleContext(any(), any()))
                .thenAnswer(invocation -> {
                    // Ensure that the passed lambda is executed
                    @SuppressWarnings("unchecked")
                    org.springframework.ldap.core.ContextExecutor<LdapContext> executor =
                            (org.springframework.ldap.core.ContextExecutor<LdapContext>) invocation.getArgument(1);
                    // Simulate execution of the passed lambda method
                    return executor.executeWithContext(mock(LdapContext.class)); 
                });

        // Inject the processor using reflection if needed
        try (MockedStatic<PagedResultsDirContextProcessor> processorMock = mockStatic(PagedResultsDirContextProcessor.class)) {
            processorMock.when(() -> new PagedResultsDirContextProcessor(pageSize)).thenReturn(processor);

            // Execute
            List<LDAPUserInfoDto> result = ldapGroupsService.getAllADUsers(searchFilter, pageSize);

            // Assert
            assertNotNull(result);
            assertEquals(1, result.size());
            assertEquals("user1", result.get(0).getEmpId());
        }
    }
}
