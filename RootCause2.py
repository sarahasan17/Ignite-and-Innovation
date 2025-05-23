@Override
public List<HpuSolutionType> getActiveByNameAndIGIdandCode(String name, Long investorGroupld, String typCd, Long ida) {
    Session session = getSession();

    // Fetch VersionHist with versionNum = 1 and matching ida
    Criteria versionHistCriteria = session.createCriteria(VersionHist.class);
    versionHistCriteria.add(Restrictions.eq("appFlwTyp.appFlwTypld", ida));
    versionHistCriteria.add(Restrictions.eq("versionNum", 1L));

    List<VersionHist> versionHists = versionHistCriteria.list();

    if (versionHists == null || versionHists.isEmpty()) {
        return new ArrayList<>();
    }

    Encoder esapiEncoder = DefaultEncoder.getInstance();
    String sanitizedName = esapiEncoder.encodeForSQL(new OracleCodec(), name);
    String sanitizedTypeCd = esapiEncoder.encodeForSQL(new OracleCodec(), typCd);

    Criteria criteria = session.createCriteria(HpuSolutionType.class);
    criteria.add(Restrictions.eq("name", sanitizedName));
    criteria.add(Restrictions.eq("investorGroup.investorGroupld", investorGroupld));
    criteria.add(Restrictions.eq("typCd", sanitizedTypeCd));
    criteria.add(Restrictions.eq("isActive", Constants.Y));
    criteria.add(Restrictions.eq("versionHist.versionHistId", versionHists.get(0).getVersionHistId()));

    // Correct the SQL formula for ordering
    criteria.addOrder(Order.sqlFormula("REPLACE(REPLACE(SOLUTION_TYP_NM, '-', ''), ' ', '')"));

    return criteria.list();
}






@Test
void testSimoLienTypesJsonConversion_throwsException() throws JsonProcessingException {
    // Arrange
    ObjectMapper mockObjectMapper = Mockito.mock(ObjectMapper.class);
    List<String> simorLienTypes = Arrays.asList("Type1", "Type2");

    // Simulate exception
    Mockito.when(mockObjectMapper.writeValueAsString(simorLienTypes))
           .thenThrow(new JsonProcessingException("Mock JSON error") {});

    // Use a spy or mock to override the Mapper.INSTANCE.getObjectMapper() call
    // This requires some trick depending on how Mapper.INSTANCE is designed

    // For illustration, let's assume Mapper.INSTANCE is a singleton and replaceable
    Mapper mockMapper = Mockito.mock(Mapper.class);
    Mockito.when(mockMapper.getObjectMapper()).thenReturn(mockObjectMapper);

    // Use a setter or reflection to inject mockMapper into your service (if possible)
    // For example:
    MyService service = new MyService();
    service.setMapper(mockMapper); // Or use reflection if no setter

    // Act
    service.yourMethodUnderTest(); // The method containing the try-catch block

    // Assert (you can verify logs or state changes if needed)
    // For example, check that simoLienType was not set or logged appropriately
}
