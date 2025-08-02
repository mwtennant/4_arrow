# Phase 2 Cleanup Schedule - Role Terminology Migration

**Target Date:** 90 days after Phase User completion (approximately 2025-10-28)
**Phase User Completion:** 2025-07-30

## Cleanup Tasks

### 1. Remove Deprecated Code
- [ ] **Remove `is_member` property** from `User` model in `core/models.py`
- [ ] **Remove `--member` CLI flag** support from `main.py`
- [ ] **Remove legacy shim** functions from `utils/legacy_shim.py`
- [ ] **Remove compatibility tests** from `tests/test_role_helpers.py`

### 2. Database Cleanup
- [ ] **Drop legacy columns** if any `is_member` columns exist in database
- [ ] **Update migration script** to remove rollback capability for cleaned up features
- [ ] **Archive migration logs** and create final migration report

### 3. Documentation Updates
- [ ] **Update ADR-008** to reflect completion of Phase 2
- [ ] **Archive migration guide** to historical documentation
- [ ] **Update API documentation** to remove legacy field references
- [ ] **Update CLI help text** to remove deprecation notices

### 4. External Integration
- [ ] **Notify external system owners** of upcoming JSON format changes
- [ ] **Update integration documentation** to require new role field
- [ ] **Remove backward compatibility** from API responses
- [ ] **Test external system compatibility** with role-only format

### 5. Code Quality
- [ ] **Run regex guard tests** to ensure no legacy terminology remains
- [ ] **Update code style guide** to include role terminology standards
- [ ] **Perform security review** of new role-based permissions
- [ ] **Update performance benchmarks** with role-based queries

## Pre-Cleanup Verification

Before executing Phase 2 cleanup, verify:

1. **All deprecation warnings addressed** in active codebases
2. **External systems migrated** to use role field
3. **No production systems** still depend on legacy APIs
4. **Team trained** on new role terminology and methods
5. **Migration documentation** archived for future reference

## Cleanup Execution Plan

### Week 1: Preparation
- Notify stakeholders of upcoming changes
- Verify external system compatibility
- Create rollback plan for critical issues

### Week 2: Code Cleanup  
- Remove deprecated properties and methods
- Update CLI flag handling
- Clean up test files

### Week 3: Database & API
- Execute database cleanup scripts
- Remove JSON compatibility layer
- Update API documentation

### Week 4: Verification & Documentation
- Run full test suite
- Update documentation
- Archive migration materials

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| External system breaks | High | Thorough pre-cleanup verification, rollback plan |
| Legacy code still in use | Medium | Comprehensive regex guards, team notification |
| Performance regression | Low | Performance benchmarks, monitoring |
| Documentation gaps | Low | Systematic doc review process |

## Success Criteria

Phase 2 cleanup is successful when:
- ✅ All deprecated code removed
- ✅ No legacy terminology in active codebase  
- ✅ All external systems use new role format
- ✅ Performance maintained or improved
- ✅ Documentation fully updated
- ✅ Team fully transitioned to new terminology

## Rollback Plan

If critical issues arise during cleanup:

1. **Immediate**: Revert most recent changes via version control
2. **Database**: Restore from pre-cleanup backup
3. **API**: Re-enable compatibility layer temporarily  
4. **External**: Coordinate emergency response with integration owners
5. **Timeline**: Extend cleanup period and re-assess dependencies

## Post-Cleanup

After Phase 2 completion:
- Update team onboarding materials
- Create case study for future migrations
- Document lessons learned
- Archive all migration-related materials
- Celebrate successful terminology standardization! 🎉

---

**Scheduled by:** Claude Code AI Assistant  
**Review Date:** 2025-10-01 (4 weeks before execution)  
**Owner:** Development Team Lead  
**Stakeholders:** All system integrators and external API consumers